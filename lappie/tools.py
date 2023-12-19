import types
from typing import Callable
from openbb import obb
from functools import wraps

from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores import FAISS, VectorStore


# Voodoo magic
def use_custom_docstring(docstring):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs).results
        wrapper.__doc__ = docstring
        wrapper.__annotations__ = func.__annotations__
        return wrapper
    return decorator

def _get_description(command_info_dict):
    outputs_str = "\n"
    for name, fieldinfo in command_info_dict['output'].model_fields.items():
        outputs_str += name + " - " + fieldinfo.description + "\n" #+ f"when provider one of [{fieldinfo.title}]\n"

    description = command_info_dict['callable'].__doc__.split("\n")[0]
    description += "\nOutputs:\n" + outputs_str
    return description

def openbb_endpoint_to_magentic(endpoint_route):
    command_info_dict = obb.coverage.command_schemas()[endpoint_route]
    return get_magentic_compatible_openbb_tool(command_info_dict)

def copy_func(f, name=None):
    new_func = types.FunctionType(
        f.__code__, f.__globals__, name or f.__name__, f.__defaults__, f.__closure__
    )
    new_func.__annotations__ = f.__annotations__
    new_func.__doc__ = "blah di blah"
    return new_func

def get_magentic_compatible_openbb_tool(command_info_dict: dict) -> Callable:
    func = command_info_dict['callable']
    wrapped_func = use_custom_docstring("Blah di blah")(func)
    return wrapped_func


def get_openbb_tool_info(function_name: str, command_info_dict: dict) -> dict:
    input_model = command_info_dict['input']
    function = command_info_dict['callable']

    outputs_str = "\n"
    for name, fieldinfo in command_info_dict['output'].model_fields.items():
        outputs_str += name + " - " + fieldinfo.description + "\n" #+ f"when provider one of [{fieldinfo.title}]\n"

    description = function.__doc__.split("\n")[0]
    description += "\nOutputs:\n" + outputs_str

    return {
        "name": function_name,
        "description": description,
        "input_model": input_model
    }


def get_all_openbb_tools_info() -> list[dict]:
    openbb_tools_info = []
    for endpoint, info_dict in obb.coverage.command_schemas().items():
        tool_info = get_openbb_tool_info(function_name=endpoint, command_info_dict=info_dict)
        openbb_tools_info.append(tool_info)

    return openbb_tools_info


def create_tool_index(tools: list[dict]) -> VectorStore:
    docs = [
        Document(page_content=t['description'], metadata={'index': i})
        for i, t in enumerate(tools)
    ]

    vector_store = FAISS.from_documents(docs, OpenAIEmbeddings())
    return vector_store
