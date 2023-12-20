from magentic import FunctionCall, OpenaiChatModel, chatprompt, SystemMessage, FunctionResultMessage, UserMessage, AssistantMessage
from magentic.chat_model.message import Message
from pydantic import BaseModel


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
    return local_vars['dynamic_chain']


def get_input_variables(messages):
    args = []
    for message in messages:
        if isinstance(message.content, str):
            opening_brackets = [i for i, s in enumerate(message.content) if s == '{']
            closing_brackets = [i for i, s in enumerate(message.content) if s == '}']

            for start, end in zip(opening_brackets, closing_brackets):
                args.append(message.content[start+1:end])
    return args


def make_chain(messages, functions=None, output_model=None):
    input_variables = get_input_variables(messages)
    chain = create_function(input_variables, output_model)
    decorated_chain = chatprompt(*messages, functions=functions)(chain)
    return decorated_chain


def make_agent(
        messages: list[Message],
        functions=None
):
    def agent(**kwargs):
        chain = make_chain(messages=messages, functions=functions)
        result = chain(**kwargs)
        while isinstance(result, FunctionCall):
            breakpoint()
            function_call: FunctionCall = result
            function_result = FunctionResultMessage(content=function_call(), function_call=function_call)

            # Update the messages
            messages.append(function_result)
            breakpoint()
            chain = make_chain(messages=messages, functions=functions)
            result = chain(**kwargs)
        return result

    return agent
