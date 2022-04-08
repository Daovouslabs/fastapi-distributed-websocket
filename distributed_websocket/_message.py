import json
from typing import Any

from .utils import update


def tag_client_message(data: dict, topic: str | None = None) -> Any:
    if not topic:
        return update(data, **{'type': 'broadcast', 'topic': None})
    return update(data, **{'type': 'send', 'topic': topic})


def untag_broker_message(data: dict | str) -> Any:
    if isinstance(data, str):
        data: dict = json.loads(data)
    return data.pop('type'), data.pop('topic'), data
