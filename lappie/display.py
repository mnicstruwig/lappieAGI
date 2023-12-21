from rich.text import Text
from rich.tree import Tree
from rich.console import Console, Group
from rich.panel import Panel


from lappie.tree import find_subquestion
from .models import ActionResponse, Action


# def display_subquestion(subquestion: Union[SubQuestion, World], prefix="  ") -> str:
#     display_str = prefix + " ➡️  Question: " + str(subquestion.question) + "\n"
#     display_str += prefix + f"    ({subquestion.id})\n"

#     if subquestion.answer is not None:
#         emoji = "✅"
#     else:
#         emoji = "🕑"

#     display_str += prefix + f"   {emoji} Answer: " + str(subquestion.answer) + "\n"

#     for subquestion in subquestion.subquestions:
#         display_str += display_subquestion(subquestion, prefix=prefix + "  ")

#     return display_str
#


def display_intro():
    out = """\
               `           '
                `         '
                 :       :
___              `       '              ___
`Y8888ba.         :     :         .ad8888P'
  88888888b.      `     '      .d88888888
  8888888888b.     :   :     .d8888888888
  88888P'  `?8b.   `   '   .d8P'  `?88888
  88888       "8b   : :   d8"       88888
 j88888  .db.   ?b       dP   .db.  88888k
   `888  8888    `b ( ) d'    8888  888'
    888. ?88P                 ?88P .888
    8888  ""        / \        ""  8888
    8888b.   _,aaY' | | `Yaa,_   .d8888
   j8888888888f"'   \ /    `"?888888888k
      88888'.'      d b       `.`8888
      88' .8       d' `b       8. `88
      f  .88 db   d'| |`b   db 88.  l
         888 `'   8 | | 8   `' 88b
         888      8 | | 8      888
        d888b   .d8 \_/ 8b.   d888b
        88888888888     88888888888
        8888888888       8888888888
        f 8888888'       `8888888 l
          `888888         888888'
           8P  `Y         Y'  ?8
           8                   8
           f                   l

    Welcome to LappieAGI!

    Loading...
    """
    print(out)


def build_answer(answer):
    if answer:
        style = "white"
        prefix = "✅\n"
        text = Text(prefix + answer, style=style)
    else:
        style = "dim"
        prefix = "🕑 Pending"
        text = Text(prefix, style=style)
    return text


def build_id(id_):
    return Text(f"({id_})", style="italic dim")


def build_question_panel(question):
    if question.answer:
        prefix = "🦋"
    else:
        prefix = "🕑"

    subquestion_title_text = Text(f"{prefix} {question.question}")
    subquestion_title_text.append("\n")
    subquestion_title_text.append("\n")
    subquestion_title_text.append(
        Text(str(question.answer), style="answer" if question.answer else "dim")
    )
    subquestion_title_text.append("\n")
    subquestion_title_text.append("---", style="dim")
    subquestion_title_text.append("\n")
    subquestion_title_text.append(build_id(question.id))
    border_style = "green" if question.answer else "white"
    main_panel = Panel.fit(subquestion_title_text, border_style=border_style)
    group = Group(main_panel)
    return group


def build_current_action(action: ActionResponse | None, target_question):
    if not action:
        return Text("...")
    if action.action == Action.ADD:
        prefix = "➕"
    elif action.action == Action.ANSWER:
        prefix = "🔮"
    else:
        prefix = "?"

    text = Text(f"Action: {prefix} {action.action.value}\n", style="bold")
    text.append(Text(f"Question: {target_question.question}\n", style="bold"))
    text.append(Text(f"Thoughts: 💭 {action.guidance}", style="bold"))
    return text


def render(world, current_action=None):
    group = Group(
        build_current_action(
            current_action,
            target_question=find_subquestion(world, current_action.target_question_id),
        ),
        Text("-----"),
        build_tree(world),
    )
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

    if not root:
        text = Text(f"✨ Question: {question.question}", style="bold")
        text.append("\n")
        text.append(build_answer(question.answer))
        root = Tree(text)
    else:
        group = build_question_panel(question)
        root = root.add(group)

    for subquestion in question.subquestions:
        build_tree(subquestion, root=root)

    return root
