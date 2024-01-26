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


def test_parse_final_answer():
    test_str = """{\n    "answer": "The key differences in the financial results and management comments in the most recent AAPL and TSLA transcripts are as follows:\n\nFor AAPL:\n- Revenue: $117.2 billion for Q1 FY2023, down 5% year-over-year.\n- iPhone revenue: $65.8 billion for the quarter, down 8% year-over-year.\n- Mac revenue: $7.7 billion, in line with expectations.\n- iPad revenue: $9.4 billion, up 30% year-over-year.\n- Wearables, Home and Accessories revenue: $13.5 billion, down 8% year-over-year.\n- Services revenue: $20.8 billion, an all-time record.\n- Net income: $30 billion.\n- Diluted earnings per share: $1.88.\n- Operating cash flow: $34 billion.\n- Active devices: Over 2 billion.\n- Paid subscriptions: More than 935 million.\n\nFor TSLA (not directly provided in the observation but can be inferred from the context):\n- The focus was on the launch of the Vision Pro, a new product set to release early next year.\n- The discussion included the importance of the Chinese market and the record iPhone revenue in India.\n- The commentary highlighted the all-time revenue record in Services and the growth in the installed base of active devices.\n- The financial performance of Mac and iPad was compared to the previous year, noting the supply disruptions and subsequent demand recapture.\n- The Wearables, Home and Accessories category was mentioned, with a focus on the Apple Watch and its expansion.\n- The Services segment was emphasized, with records set across App Store, advertising, AppleCare, iCloud, payment services, and video.\n\nThe contrast between the two transcripts shows that AAPL focused on detailed financial performance across various product categories and services, while TSLA\'s transcript (inferred from context) highlighted new product announcements and strategic market focuses.",\n    "comments": "The observation provides detailed information from the AAPL earnings call transcript but does not directly include the TSLA transcript. However, based on the context and the fact that TSLA was mentioned in relation to the Vision Pro launch and other strategic focuses, a contrast can be drawn between the two companies\' most recent earnings call transcripts. AAPL provided a comprehensive breakdown of financial results across different product lines and services, while TSLA\'s discussion (inferred) seemed to revolve around new product launches and market strategies."\n}"""
#    test_str = """{\n "answer": "My\nanswer"}"""
#
#
    test_str = """
    {
       "answer": "my\nanswer",
       "comment": "my_comment"
    }
    """

    actual_result = agent._react_parse_final_answer_response(test_str)
    # TODO: Write test
    assert False
