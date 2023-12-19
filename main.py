from lappie.llm import next_step

from lappie.models import Action, World
from lappie.display import print_world
from lappie.tree import add_subquestion, answer_question, delete_subquestion



def main_loop(query: str):
    world = World(
        question=query
    )

    action = next_step(world_state=world.model_dump_json())

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
            break
        if action.action == Action.DELETE:
            world: World = delete_subquestion(world, action.target_question_id)

        print_world(world)
        action = next_step(world_state=world.model_dump_json())
        print("=======")
        print(action)

main_loop("Who has the highest stock price? AMZN or TSLA?")
