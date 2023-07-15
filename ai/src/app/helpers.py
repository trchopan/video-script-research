import datetime
from functools import wraps

from flask import request
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, PromptValue


class BadRequestException(Exception):
    pass


def request_query_require_validate(fields: list[str]):
    field_values = []
    for field in fields:
        field_value = request.args.get(field, None)
        if field_value is None:
            raise BadRequestException(f"Bad request. Missing field: {field}")

        field_values.append(field_value)

    return field_values


def request_json_require_validate(fields: list[str]):
    if request.json is None:
        raise BadRequestException("Bad request. Body is None")

    field_values = []
    for field in fields:
        field_value = request.json.get(field, None)
        if field_value is None:
            raise BadRequestException(f"Bad request. Missing field: {field}")

        field_values.append(field_value)

    return field_values


def request_json_optional(fields: list[str]):
    field_values = []
    for field in fields:
        field_values.append(
            request.json.get(field, None) if request.json is not None else None
        )

    return field_values


def with_handle_require_validate(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            resp_msg, status = func(*args, **kwargs)
            return resp_msg, status
        except BadRequestException as e:
            return str(e), 400

    return decorated_function


def find_element(array, condition):
    for element in array:
        if condition(element):
            return element
    return None


def get_timestamp():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


def send_chat_prompt_with_print(chat: ChatOpenAI, prompt: PromptValue) -> BaseMessage:
    print(">>>>")
    for m in prompt.to_messages():
        print(m.content)

    result = chat(prompt.to_messages())
    print(result.content)
    print("===")
    return result
