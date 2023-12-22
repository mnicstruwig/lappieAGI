"""LLM and agentic components."""
from typing import Callable
from langchain.vectorstores import VectorStore
from magentic import prompt, prompt_chain
from magentic.chat_model.openai_chat_model import OpenaiChatModel


from .prompts import (
    NEW_SUBQUESTION_PROMPT,
    ANSWER_SUBQUESTION_PROMPT,
    SEARCH_TOOLS_PROMPT,
    REACT_PROMPT,
)
from .models import ActionResponse, AnswerResponse, RetrievedTool, Tool
from .tools import openbb_endpoint_to_magentic, search_tool_index


def search_tools(
    world_state: str, question_id: str, tool_index: VectorStore, tools: list[Tool]
) -> list[Callable]:
    """Retrieve magentic-compatible tools from a tool index."""

    def query_tool_index(query: str) -> list[dict]:
        fetched_tools = search_tool_index(
            vector_index=tool_index, tools=tools, query=query
        )

        # Save on tokens by only responding with the name and first line of the description
        # for each retreived tool.
        for tool in fetched_tools:
            tool["description"] = tool["description"].split("\n")[0]
        return fetched_tools

    @prompt_chain(
        SEARCH_TOOLS_PROMPT,
        functions=[query_tool_index],
        model=OpenaiChatModel(model="gpt-4-1106-preview"),
    )
    def _search_tools(world_state: str, question_id: str) -> list[RetrievedTool]:
        ...

    retrieved_tool_names = _search_tools(
        world_state=world_state, question_id=question_id
    )
    tool_names = [t.name for t in retrieved_tool_names]
    magentic_compatible_tools = [
        openbb_endpoint_to_magentic(name) for name in tool_names
    ]
    return magentic_compatible_tools


@prompt(
    REACT_PROMPT,
    model=OpenaiChatModel(model="gpt-4-1106-preview", max_tokens=512),
    stop=["END"]
)
def next_step(
    world_state: str, action_schema: str = str(ActionResponse.model_json_schema())
) -> str:
    """This is a faux React agent, since we don't currently keep state between runs!"""
    ...


def answer_question(
    world_state: str, question_id: str, functions: list[Callable] | None
) -> AnswerResponse:
    @prompt_chain(
        ANSWER_SUBQUESTION_PROMPT,
        functions=functions,
        model=OpenaiChatModel(model="gpt-4-1106-preview"),
    )
    def _answer_question(world_state: str, question_id: str) -> AnswerResponse:
        ...

    return _answer_question(world_state=world_state, question_id=question_id)


@prompt_chain(
    NEW_SUBQUESTION_PROMPT,
    model=OpenaiChatModel(model="gpt-4-1106-preview"),
)
def add_subquestion(
    world_state: str, question_id: str, guidance: str | None = None
) -> str:
    """Use an agent to generate a new subquestion with parent subquestion id `parent_id` in `world`."""
    ...


@prompt_chain(NEW_SUBQUESTION_PROMPT, model=OpenaiChatModel(model="gpt-4-1106-preview"))
def update_subquestion(world_state: str, question_id: str, guidance: str | None) -> str:
    """Use an agent to update a subquestion with parent id `parent_id` in world."""
    ...
