from enum import Enum
from typing import Callable, Optional, Any
from uuid import uuid4
from pydantic import UUID4, BaseModel, Field


class SubQuestion(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)
    question: str = Field(description="The question.")
    answer: Optional[str] = Field(description="The answer to the question", default=None)
    human_feedback: Optional[str] = Field(description="Feedback provided by the human to assist with answering the question.", default=None)
    subquestions: list["SubQuestion"] = Field(description="A list of subquestions that, when answered, will assist with answering the current question.", default=[])


class NewSubQuestion(BaseModel):
    parent_id: str
    subquestion: SubQuestion


class World(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)
    question: str = Field(description="The main question.")
    answer: Optional[str] = Field(description="The answer to the main question", default=None)
    human_feedback: Optional[str] = Field(description="Feedback provided by the human to assist with answering the question.", default=None)
    subquestions: list["SubQuestion"] = Field(description="A list of subquestions that, when answered, will assist with answering the current question.", default=[])


class Tool(BaseModel):
    name: str
    description: str
    function: Callable
    input_model: Any = Field(description="Pydantic model to use for input arguments.")


class Action(str, Enum):
    ADD = "add"
    ANSWER = "answer"
    DELETE = "delete"
    UPDATE = "update"
    PROMPT_HUMAN = "prompt_human"
    FINAL_ANSWER = "final_answer"
    STOP = "stop"


class ActionResponse(BaseModel):
    action: Action = Field(description="The action to take.")
    target_question_id: str = Field(
        description="The question ID to target for the specific action."
    )
    guidance: str | None = Field(
        description="Motivation for performing the action. Helpful for downstream assistants who will perform the action.",
        examples=["The subquestion is too vague and needs to be refined."],
        default=None,
    )


class AnswerResponse(BaseModel):
    answer: str = Field(description="The answer to the question.")
    comments: Optional[str] = Field(
        description="Additional commentary, as required by the agent.", default=None
    )


class RetrievedTool(BaseModel):
    name: str = Field(description="The name of the tool.")
