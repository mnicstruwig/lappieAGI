from typing import Any, Callable
from magentic import (
    FunctionCall,
    OpenaiChatModel,
    chatprompt,
    SystemMessage,
    FunctionResultMessage,
    UserMessage,
    AssistantMessage,
)
from magentic.chat_model.message import Message
from pydantic import BaseModel

from lappie.prompts import BASE_REACT_PROMPT

import inspect
from pydantic import BaseModel, create_model


def create_pydantic_model_from_function(fn):
    sig = inspect.signature(fn)
    fields = {
        param.name: (param.annotation, ...)
        if param.default is param.empty
        else (param.annotation, param.default)
        for param in sig.parameters.values()
    }
    return create_model(fn.__name__ + "Model", **fields)  # type: ignore


def create_function(args=None, output_model: type[BaseModel] | None = None):
    globals_copy = globals().copy()
    args_str = ""  # default
    if args:
        args_str = ""
        for arg in args:
            args_str += arg + ": str, "

    output_str = "str"  # default
    if output_model:
        output_str = output_model.__name__
        # Make sure the model is available in the globals namespace
        globals_copy[output_model.__name__] = output_model

    code = f"def dynamic_chain({args_str}) -> {output_str}:\n    ..."
    local_vars = {}

    exec(code, globals_copy, local_vars)
    return local_vars["dynamic_chain"]


def get_input_variables(messages):
    args = []
    for message in messages:
        if not isinstance(message, AssistantMessage) and isinstance(
            message.content, str
        ):
            opening_brackets = [i for i, s in enumerate(message.content) if s == "{"]
            closing_brackets = [i for i, s in enumerate(message.content) if s == "}"]

            for start, end in zip(opening_brackets, closing_brackets):
                args.append(message.content[start + 1 : end])
    return args


def make_chain(
    messages,
    functions=None,
    output_model=None,
    stop=None,
    model=OpenaiChatModel(model="gpt-4-1106-preview"),
):
    input_variables = get_input_variables(messages)
    chain = create_function(input_variables, output_model)
    decorated_chain = chatprompt(
        *messages, functions=functions, stop=stop, model=model
    )(chain)
    return decorated_chain


def make_agent(
    messages: list[Message],
    functions=None,
    stop: list[str] | None = None,
):
    def agent(**kwargs):
        chain = make_chain(messages=messages, functions=functions)
        result = chain(**kwargs)
        while isinstance(result, FunctionCall):
            function_call: FunctionCall = result
            function_result = FunctionResultMessage(
                content=function_call(), function_call=function_call
            )

            # Update the messages
            messages.append(function_result)
            chain = make_chain(messages=messages, functions=functions, stop=stop)
            result = chain(**kwargs)
        return result

    return agent


def _render_tools_and_descriptions(tools: dict[str, dict[str, Any]]):
    tool_str = ""
    for name, tool in tools.items():
        tool_str += f"name: {name}\n"
        tool_str += f"schema: {tool['args_schema'].model_json_schema()}\n"
    return tool_str


def _prepare_tools(functions: list[Callable] | None) -> dict:
    tools = {}
    if functions:
        tools = {
            function.__name__: {
                "callable": function,
                "args_schema": create_pydantic_model_from_function(function),
            }
            for function in functions
        }
    return tools


def make_react_agent(
    prompt: str,
    functions=None,
):
    messages = [SystemMessage(BASE_REACT_PROMPT), UserMessage(prompt)]

    stop = ["Observation:"]

    tools = _prepare_tools(functions)
    tools_and_description = _render_tools_and_descriptions(tools)

    def agent(tools_and_descriptions=tools_and_description, **kwargs):
        # The react agent is a bit different -- we need to do the function calling manually
        chain = make_chain(messages=messages, stop=stop)
        result = chain(tools_and_descriptions=tools_and_descriptions, **kwargs)
        while "Final Answer:" not in result:
            # Append the requested action and its input...
            sanitized_result = result.replace("{", "{{").replace("}", "}}")
            messages.append(AssistantMessage(sanitized_result))

            # Perform the requested action...
            action = result.split("Action: ")[-1].split("\n")[0]
            action_input = result.split("Action Input: ")[-1].split("\n")[0]
            input_object = tools[action]["args_schema"].parse_raw(
                action_input
            )  # we do this for validation
            function_call_result = tools[action]["callable"](
                **input_object.model_dump()
            )

            # Append the observation / result...
            messages.append(UserMessage(f"Observation: {str(function_call_result)}"))

            # ... continue
            chain = make_chain(messages=messages, stop=stop)
            result = chain(tools_and_descriptions=tools_and_descriptions, **kwargs)

        # Parse the final answer
        final_answer = result.split("Final Answer: ")[-1]
        return final_answer

    return agent
