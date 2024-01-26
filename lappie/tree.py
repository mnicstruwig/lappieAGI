import json
from typing import Union, Optional
from lappie.agent import react_agent

from lappie.tools import (
    create_tool_index,
    get_all_openbb_tools,
)
from .models import ActionResponse, World, SubQuestion
from . import llm

tools = get_all_openbb_tools()
tool_index = create_tool_index(tools)


def _parse_next_step_response(response: str) -> ActionResponse:
    try:
        json_str = response.strip().split("Action:")[-1].strip()
        json_str = json_str.replace("```json", "")
        json_str = json_str.replace("```", "")
        start_index = json_str.find("{")
        end_index = json_str.rfind("}")
        action_dict = json.loads(json_str[start_index : end_index + 1])
        action_response = ActionResponse(**action_dict)
    except Exception as err:
        breakpoint()
        print(err)
        raise (err)
    return action_response


def find_subquestion(
    obj: Union[World, SubQuestion], question_id: str
) -> Optional[Union[World, SubQuestion]]:
    if str(obj.id) == str(question_id):
        return obj

    for subquestion in obj.subquestions:
        if str(subquestion.id) == str(question_id):
            return subquestion
        elif subquestion.subquestions:
            result = find_subquestion(subquestion, question_id)
            if result:
                return result


def get_next_step(world: World) -> ActionResponse:
    response = llm.next_step(world_state=world.model_dump_json())
    action_response = _parse_next_step_response(response)
    return action_response


def answer_question(world: World, question_id: str) -> World:
    """Generate an answer to a (sub)question using an agent.

    The question to be answered is specified using `question_id`.

    Note that a new copy of the world is returned.
    """
    world = world.model_copy()
    target = find_subquestion(world, question_id)
    if target:
        # Fetch tools
        fetched_tools = []
        if isinstance(target, (SubQuestion)):
            print("Fetching tools...")
            fetched_tools = llm.search_tools(
                world_state=world.model_dump_json(),
                question_id=question_id,
                tool_index=tool_index,
                tools=tools,
            )
            print("Fetched tools: ", [tool.__name__ for tool in fetched_tools])

        print("Answering question: ", question_id)

        # This much match the format of the prompt
        query = ""
        query += f"Tree: {world.model_dump_json()}\n"
        query += f"Question ID: {question_id}\n"

        answer_response = react_agent(query=query, functions=fetched_tools)
        target.answer = answer_response.answer
    return world


def prompt_human(world: World, question_id: str, guidance: str | None) -> World:
    question = find_subquestion(world, question_id)
    if question:
        print(
            f"Agent is asking for human feedback on the following question: {question.question}"
        )
        human_feedback = input(f"{guidance}\n")
        question.human_feedback = human_feedback
    return world


def delete_subquestion(world: World, question_id: str) -> World:
    """Delete a subquestion from the world."""
    world = world.model_copy()
    subquestion = find_subquestion(world, question_id)
    del subquestion
    return world


def add_subquestion(
    world: World, question_id: str, guidance: str | None = None
) -> World:
    """Add a new subquestion to the world using an agent.

    The parent question (that must receive a subquestion) is specified using `question_id`.

    Note that a new copy of the World is returned.
    """
    world = world.model_copy()
    new_subquestion = llm.add_subquestion(
        world_state=world.model_dump_json(), question_id=question_id, guidance=guidance
    )

    if new_subquestion:
        parent = find_subquestion(world, question_id)
        if parent:
            parent.subquestions.append(SubQuestion(question=new_subquestion))
    else:
        raise ValueError("Target not found :(")
    return world


def update_question(world: World, question_id: str, guidance: str | None) -> World:
    """Update a (sub)question using an agent.

    The question to be answerd is specified using `question_id`.
    """
    world = world.model_copy()
    target = find_subquestion(world, question_id)
    if target:
        updated_subquestion_text = llm.update_subquestion(
            world_state=world.model_dump_json(),
            question_id=question_id,
            guidance=guidance,
        )
        target.question = updated_subquestion_text
        target.answer = None
    else:
        raise ValueError("Target not found")
    return world
