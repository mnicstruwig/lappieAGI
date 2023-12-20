from lappie.models import Action, World
from lappie.display import print_world
from lappie.tree import (
    add_subquestion,
    answer_question,
    delete_subquestion,
    get_next_step,
)


def main_loop(query: str):
    world = World(question=query)

    action = get_next_step(world)
    print_world(world)
    print("=======")
    print(action)

    while action.action != Action.STOP:
        if action.action == Action.ADD:
            world: World = add_subquestion(world, action.target_question_id)
        if action.action == Action.ANSWER:
            world: World = answer_question(world, action.target_question_id)
        if action.action == Action.FINAL_ANSWER:
            world: World = answer_question(world, action.target_question_id)
            print_world(world)
            break
        if action.action == Action.DELETE:
            world: World = delete_subquestion(world, action.target_question_id)

        print_world(world)
        action = get_next_step(world)
        print("=======")
        print(action)


main_loop("Look up the peers of AMZN? What is their stock price?")
