import inspect
from typing import Union
from magentic import FunctionResultMessage, SystemMessage, UserMessage, FunctionCall
from pydantic import BaseModel, Field

from lappie import agent


def test_create_pydantic_model_from_function():
    def test_func(a: int, b: str, c: Union[str, None] = "123") -> str:
        ...

    pass


def test_get_input_variables():
    messages = [
        SystemMessage("Tell me a joke about {topic} in {language}."),
        UserMessage("The joke must start with {start}."),
    ]

    expected_result = ["topic", "language", "start"]

    actual_result = agent.get_input_variables(messages)
    assert expected_result == actual_result


def test_get_input_variables_with_non_str_content():
    messages = [
        SystemMessage("Tell me a joke about {topic} in {language}."),
        UserMessage("The joke must start with {start}."),
        # The contents of the FunctionResultMessage below is irrelevant, we just don't want
        # this to trip up extracting the string variables between the {}.
        FunctionResultMessage(
            content=7, function_call=FunctionCall(function=lambda x: x + 1, x=1)
        ),
    ]

    expected_result = ["topic", "language", "start"]

    actual_result = agent.get_input_variables(messages)
    assert expected_result == actual_result


def test_create_function_without_input_args():
    args = None

    func = agent.create_function(args)
    sig = inspect.signature(func)
    assert len(sig.parameters) == 0


def test_create_function_with_input_args():
    args = ["topic_a", "topic_b"]

    func = agent.create_function(args)
    sig = inspect.signature(func)

    assert sig.parameters.get("topic_a")
    assert sig.parameters.get("topic_b")


def test_create_function_with_output_model():
    args = ["a", "b"]

    class TestOutputModel(BaseModel):
        expression: str = Field(description="The expression that was answered.")
        result: int = Field(description="The final answer of the expression.")

    func = agent.create_function(args, TestOutputModel)
    sig = inspect.signature(func)
    assert (
        sig.return_annotation.model_json_schema() == TestOutputModel.model_json_schema()
    )


def test_make_chain_with_input_args():
    chain = agent.make_chain(
        messages=[
            SystemMessage(
                "You are a maths robot. Give only the answer, and nothing else."
            ),
            UserMessage("Give the answer to the following equation: {equation}"),
        ],
    )

    joke = chain(equation="2+3")
    assert joke == "5"


def test_make_chain_with_function_calls():
    def topic_generator() -> str:
        return "fish"

    chain = agent.make_chain(
        messages=[
            SystemMessage(
                "You are a jokester robot. Call the function to get a topic."
            ),
        ],
        functions=[topic_generator],
    )

    function_call = chain()
    assert function_call() == "fish"


def test_make_chain_with_output_model():
    class JokeOutputModel(BaseModel):
        setup: str = Field(description="The setup of the joke")
        punchline: str = Field(description="The punchline of the joke")

    chain = agent.make_chain(
        messages=[
            SystemMessage(
                "You are a jokester robot. Tell me a joke. Stick to the output format!"
            ),
        ],
        output_model=JokeOutputModel,
    )

    result = chain()
    assert isinstance(result, JokeOutputModel)


def test_make_chain_with_stop():
    chain = agent.make_chain(
        messages=[
            SystemMessage(
                """\
                You are a helpful bot that does what you're told and is very helpful.

                Your task is to generate numbers up to a maximum specified by the user.

                Example
                -------
                user input: 5

                Your response:

                one: first
                two: second
                three: third
                four: fourth
                five: fifth
                """
            ),
            UserMessage("user input: {number}"),
        ],
        stop=["three"],
    )

    result = chain(number="5")
    assert result == "one: first\ntwo: second\n"
    breakpoint()


def test_agent():
    def add(a: int, b: int) -> int:
        """Add together two numbers."""
        return a + b

    test_agent = agent.make_agent(
        messages=[
            SystemMessage(
                "You are a maths robot. Use the provided tools to add together two provided numbers. Return only the answer, and nothing else."
            ),
            UserMessage(
                "The first number is: {first_number}.\nThe second number is {second_number}."
            ),
        ],
        functions=[add],
    )

    result = test_agent(first_number=3, second_number=4)
    assert result == "7"


def test_react_agent():
    def add(a: int, b: int) -> int:
        """Add together two numbers"""
        return a + b

    def multiply(a: int, b: int) -> int:
        """Multiply together two numbers"""
        return a * b

    result = agent.react_agent(
        query="Add together 3 and 5, then multiply by 10, then multiply by 10 again. Give only the final answer, and nothing else.",
        functions=[add, multiply],
    )

    assert result == "800"
