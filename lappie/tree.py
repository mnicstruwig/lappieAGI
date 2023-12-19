from typing import Callable, Union, Optional

from lappie.tools import create_tool_index, get_all_openbb_tools
from .models import NewSubQuestion, World, SubQuestion
from . import llm

tools = get_all_openbb_tools()
tool_index = create_tool_index(tools)

def find_subquestion(obj: Union[World, SubQuestion], question_id: str) -> Optional[Union[World, SubQuestion]]:
    if str(obj.id) == str(question_id):
        return obj

    for subquestion in obj.subquestions:
        if str(subquestion.id) == str(question_id):
            return subquestion
        if subquestion.subquestions:
            return find_subquestion(subquestion, question_id)



def answer_question(world: World, question_id: str) -> World:
    """Generate an answer to a (sub)question using an agent.

    The question to be answered is specified using `question_id`.

    Note that a new copy of the world is returned.
    """
    world = world.model_copy()
    target = find_subquestion(world, question_id)
    if target:
        # Fetch tools
        print("fetching tools...")
        fetched_tools = llm.search_tools(world_state=world.model_dump_json(), question_id=question_id, tool_index=tool_index, tools=tools)
        print("Fetched tools")
        answer_response = llm.answer_question(world_state=world.model_dump_json(), question_id=question_id)
        target.answer = answer_response.answer
    return world

def delete_subquestion(world: World, question_id: str) -> World:
    """Delete a subquestion from the world."""
    world = world.model_copy()
    subquestion = find_subquestion(world, question_id)
    del(subquestion)
    return world


def add_subquestion(world: World, question_id: str) -> World:
    """Add a new subquestion to the world using an agent.

    The parent question (that must receive a subquestion) is specified using `question_id`.

    Note that a new copy of the World is returned.
    """
    world = world.model_copy()
    new_subquestion = llm.add_subquestion(world_state=world.model_dump_json(), question_id=question_id)

    if new_subquestion:
        parent = find_subquestion(world, question_id)
        if parent:
            parent.subquestions.append(SubQuestion(question=new_subquestion))
    else:
        raise ValueError("Target not found :(")
    return world
