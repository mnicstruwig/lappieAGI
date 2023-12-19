"""LLM and agentic components."""

from functools import wraps
from langchain.vectorstores import VectorStore
from openbb import obb
from magentic import chatprompt, SystemMessage, UserMessage, prompt, prompt_chain
from magentic.chat_model.openai_chat_model import OpenaiChatModel

from .prompts import NEW_SUBQUESTION_PROMPT, ANSWER_SUBQUESTION_PROMPT, NEXT_STEP_PROMPT, SEARCH_TOOLS_PROMPT
from .models import ActionResponse, AnswerResponse, RetrievedTool, Tool
from .tools import create_tool_index, openbb_endpoint_to_magentic, search_tool_index




def search_tools(world_state: str, question_id: str, tool_index: VectorStore, tools: list[Tool]):

    def query_tool_index(query: str) -> list[dict]:
        return search_tool_index(
            vector_index=tool_index,
            tools=tools,
            query=query
        )

    @prompt_chain(
        SEARCH_TOOLS_PROMPT,
        functions=[query_tool_index],
        model=OpenaiChatModel(model="gpt-4-1106-preview"),
    )
    def _search_tools(world_state: str, question_id: str) -> list[RetrievedTool]:
        ...

    retrieved_tools = _search_tools(world_state=world_state, question_id=question_id)
    breakpoint()
    return retrieved_tools


    # Decide if tools are sufficient

    # If not, search again

@prompt(
    NEXT_STEP_PROMPT,
    model=OpenaiChatModel(model="gpt-4"),
)
def next_step(world_state: str) -> ActionResponse:
    ...

@prompt_chain(
    ANSWER_SUBQUESTION_PROMPT,
    functions=[openbb_endpoint_to_magentic(".equity.fundamental.overview")],
    model=OpenaiChatModel(model="gpt-4-1106-preview"),
)
def answer_question(world_state: str, question_id: str) -> AnswerResponse:
    """Use an agent to answer a question with `question_id` in `world`."""
    ...

@prompt_chain(
    NEW_SUBQUESTION_PROMPT,
    model=OpenaiChatModel(model="gpt-4"),
)
def add_subquestion(world_state: str, question_id: str) -> str:
    """Use an agent to generate a new subquestion with parent subquestion id `parent_id` in `world`."""
    ...
