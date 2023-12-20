import inspect

from typing import Callable, Annotated
from openbb import obb
from functools import wraps

from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores import FAISS, VectorStore

from lappie.models import Tool


# Voodoo magic
def make_magentic_compatible(docstring):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return (
                func(*args, **kwargs)
                .to_df()
                .reset_index()
                .to_json(
                    orient="records",
                    date_format="iso",
                    date_unit="s",
                )
            )

        wrapper.__doc__ = docstring

        # Ugly hack to make sure we can only search for a single symbol at a
        # time. We do this by changing the type annotation to only be a single
        # string for the `symbol` parameter.
        annotations = wrapper.__annotations__
        if "symbol" in annotations:
            openbb_custom_param = annotations["symbol"].__metadata__[0]
            annotations["symbol"] = Annotated[str, openbb_custom_param]
            wrapper.__annotations__ = annotations
        return wrapper

    return decorator


def openbb_endpoint_to_magentic(endpoint_route):
    command_info_dict = obb.coverage.command_schemas()[endpoint_route]
    return get_magentic_compatible_openbb_tool(command_info_dict)


def get_magentic_compatible_openbb_tool(command_info_dict: dict) -> Callable:
    func = command_info_dict["callable"]
    wrapped_func = make_magentic_compatible(func.__doc__.split("\n")[0])(func)
    return wrapped_func


def get_openbb_tool(function_name: str, command_info_dict: dict) -> Tool:
    input_model = command_info_dict["input"]
    function = command_info_dict["callable"]

    outputs_str = "\n"
    for name, fieldinfo in command_info_dict["output"].model_fields.items():
        outputs_str += (
            name + " - " + fieldinfo.description + "\n"
        )  # + f"when provider one of [{fieldinfo.title}]\n"

    description = function.__doc__.split("\n")[0]
    description += "\nOutputs:\n" + outputs_str

    return Tool(
        name=function_name,
        function=function,
        description=description,
        input_model=input_model,
    )


def get_all_openbb_tools() -> list[Tool]:
    openbb_tools = []
    for endpoint, info_dict in obb.coverage.command_schemas().items():
        tool = get_openbb_tool(function_name=endpoint, command_info_dict=info_dict)
        openbb_tools.append(tool)
    return openbb_tools


def create_tool_index(tools: list[Tool]) -> VectorStore:
    docs = [
        Document(page_content=t.description, metadata={"index": i})
        for i, t in enumerate(tools)
    ]

    vector_store = FAISS.from_documents(docs, OpenAIEmbeddings())
    return vector_store


def search_tool_index(
    vector_index: VectorStore, tools: list[Tool], query: str
) -> list[dict]:
    retriever = vector_index.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.65},
    )

    docs = retriever.get_relevant_documents(query)
    if len(docs) < 3:
        retriever = vector_index.as_retriever(search_kwargs={"k": 3})
        docs = retriever.get_relevant_documents(query)

    tools = [tools[d.metadata["index"]] for d in docs]

    return [{"name": t.name, "description": t.description} for t in tools]
