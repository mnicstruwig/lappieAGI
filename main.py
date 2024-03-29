# noqa: E402
from lappie.util import display_intro

display_intro()

from lappie.display import render
from lappie.models import Action, World
from lappie.tree import (
    add_subquestion,
    answer_question,
    delete_subquestion,
    get_next_step,
    update_question,
    prompt_human,
)


def main_loop(query: str):
    world = World(question=query)
    action = get_next_step(world)

    while action.action != Action.STOP:
        render(world, action)

        if action.action == Action.ADD:
            world: World = add_subquestion(
                world, action.target_question_id, action.guidance
            )
        elif action.action == Action.ANSWER:
            world: World = answer_question(world, action.target_question_id)
        elif action.action == Action.UPDATE:
            world: World = update_question(
                world, action.target_question_id, action.guidance
            )
        elif action.action == Action.FINAL_ANSWER:
            world: World = answer_question(world, action.target_question_id)
            render(world, action)
            render(world, action)
            break
        elif action.action == Action.DELETE:
            world: World = delete_subquestion(world, action.target_question_id)
        elif action.action == Action.PROMPT_HUMAN:
            world: World = prompt_human(
                world, action.target_question_id, action.guidance
            )

        action = get_next_step(world)


main_loop("I want the annual revenue for a specific year for TSLA")
