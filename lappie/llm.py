"""LLM and agentic components."""

from functools import wraps
from openbb import obb
from magentic import chatprompt, SystemMessage, UserMessage, prompt, prompt_chain
from magentic.chat_model.openai_chat_model import OpenaiChatModel

from .prompts import NEW_SUBQUESTION_PROMPT, ANSWER_SUBQUESTION_PROMPT, NEXT_STEP_PROMPT
from .models import ActionResponse, AnswerResponse
from .tools import openbb_endpoint_to_magentic, copy_func


new_func = copy_func(obb.equity.fundamental.overview)

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
