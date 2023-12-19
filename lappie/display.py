from typing import Union
from .models import SubQuestion, World

def display_subquestion(subquestion: Union[SubQuestion, World], prefix="  ") -> str:
    display_str = prefix + " ➡️  Question: " + str(subquestion.question) + "\n"
    display_str += prefix + f"    ({subquestion.id})\n"

    if subquestion.answer is not None:
        emoji = "✅"
    else:
        emoji = "🕑"

    display_str += prefix + f"   {emoji} Answer: " + str(subquestion.answer) + "\n"

    for subquestion in subquestion.subquestions:
        display_str += display_subquestion(subquestion, prefix=prefix + "  ")

    return display_str


def print_world(world: World) -> None:
    """Display the world model."""

    print("\n")
    print(display_subquestion(world))
