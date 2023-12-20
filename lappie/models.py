from enum import Enum
from typing import Callable, Optional, Any
from uuid import uuid4
from pydantic import UUID4, BaseModel, Field


class SubQuestion(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)
    question: str
    answer: Optional[str] = None
    subquestions: list["SubQuestion"] = []


class NewSubQuestion(BaseModel):
    parent_id: str
    subquestion: SubQuestion


class World(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)
    question: str
    answer: Optional[str] = None
    subquestions: list[SubQuestion] = []


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
    FINAL_ANSWER = "final_answer"
    STOP = "stop"


class ActionResponse(BaseModel):
    action: Action = Field(description="The action to take.")
    target_question_id: str = Field(
        description="The question ID to target for the specific action."
    )


class AnswerResponse(BaseModel):
    answer: str = Field(description="The answer to the question.")
    comments: Optional[str] = Field(
        description="Additional commentary, as required by the agent.", default=None
    )


class RetrievedTool(BaseModel):
    name: str = Field(description="The name of the tool.")
