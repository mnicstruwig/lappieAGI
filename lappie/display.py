from rich.text import Text
from rich.tree import Tree
from rich.console import Console, Group
from rich.panel import Panel


from lappie.tree import find_subquestion
from .models import ActionResponse, Action, World


def build_id(id_):
    return Text(f"({id_})", style="italic dim")


# TODO: Refactor (what a mess)
def build_question_panel(question, current_action: ActionResponse | None = None):
    if question.answer:
        prefix = "🦋"
    else:
        prefix = "🕑"

    subquestion_title_text = Text(f"{prefix} {question.question}")
    subquestion_title_text.append("\n")

    if question.human_guidance:
        subquestion_title_text.append(Text(f"🧑 {question.human_guidance}"))

    subquestion_title_text.append("\n")
    subquestion_title_text.append(
        Text(f"🤖 {str(question.answer)}", style="white" if question.answer else "dim")
    )
    # subquestion_title_text.append("\n")
    # subquestion_title_text.append("---", style="dim")
    # subquestion_title_text.append("\n")
    # subquestion_title_text.append(build_id(question.id))
    border_style = "green" if question.answer else "white"

    if current_action:
        border_style = (
            "bright_blue bold"
            if str(question.id) == current_action.target_question_id
            else border_style
        )

    main_panel = Panel(subquestion_title_text, border_style=border_style, expand=False)
    group = Group(main_panel)
    return group


def build_current_action(action: ActionResponse | None, target_question):
    if not action:
        return Text("...")
    if action.action == Action.ADD:
        prefix = "➕"
    elif action.action == Action.ANSWER:
        prefix = "🔮"
    elif action.action == Action.FINAL_ANSWER:
        prefix = "🔮"
    elif action.action == Action.PROMPT_HUMAN:
        prefix = "🙋"
    else:
        prefix = "?"

    text = Text(f"Action: {prefix} {action.action.value}\n", style="bold")
    text.append(Text(f"Question: {target_question.question}\n", style="bold"))
    text.append(Text(f"Thoughts: 💭 {action.guidance}", style="bold"))
    return text


def render(world: World, current_action: ActionResponse | None = None):
    tree = build_tree(world, current_action=current_action)

    if current_action:
        display_current_action = build_current_action(
            current_action,
            target_question=find_subquestion(world, current_action.target_question_id),
        )
    else:
        display_current_action = Text("")

    group = Group(display_current_action, Text("-----"), tree)
    console = Console()
    console.clear()
    console.print(group)


def build_tree(
    question,
    root=None,
    current_action: ActionResponse | None = None,
    target_question: str | None = None,
):
    """Display the world model."""

    group = build_question_panel(question, current_action)

    if not root:
        root = Tree(group)
    else:
        root = root.add(group)

    for subquestion in question.subquestions:
        build_tree(subquestion, root=root, current_action=current_action)

    return root
