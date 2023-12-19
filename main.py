from decimal import Decimal
from typing import Union, Optional

from magentic import chatprompt, prompt, UserMessage, SystemMessage, AssistantMessage, prompt_chain
from magentic.chat_model.openai_chat_model import OpenaiChatModel
from lappie.llm import next_step

from lappie.models import Action, ActionResponse, SubQuestion, World
from lappie.prompts import MAIN_AGENT_PROMPT, NEXT_STEP_PROMPT
from lappie.display import print_world
from lappie.tools import get_openbb_tool_info, get_all_openbb_tools_info
from lappie.tree import add_subquestion, answer_question



@chatprompt(
    SystemMessage(MAIN_AGENT_PROMPT),
    UserMessage("## State:\n{world_state}"),
    functions=[add_subquestion, answer_question],
    model=OpenaiChatModel(model="gpt-4-1106-preview"),

)
def update_world(world_state) -> World:
    ...


def main_loop(query: str):
    world = World(
        question=query
    )

    action = next_step(world_state=world.model_dump_json())

    print_world(world)
    print("=======")
    print(action)

    while action.action != Action.STOP and input("Continue?") == "y":

        if action.action == Action.ADD:
            world: World = add_subquestion(world, action.target_question_id)
        if action.action == Action.ANSWER:
            world: World = answer_question(world, action.target_question_id)

        print_world(world)
        action = next_step(world_state=world.model_dump_json())
        print("=======")
        print(action)

main_loop("What is the current stock price of TSLA?")
