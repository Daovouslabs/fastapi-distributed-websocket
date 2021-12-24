import json
from typing import Optional, Any, NoReturn

from .utils import is_valid_json


def tag_client_message(data: dict, topic: Optional[str] = None) -> Any:
    if not topic:
        return data.update({'tpye': 'broadcast'})
    return data.update({'type': 'publish', 'topic': topic})


def untag_broker_message(data: str) -> Any:
    msg: dict = json.loads(data)
    return msg.pop('type'), msg.pop('topic'), msg


class Message:
    def __init__(
        self,
        topic: str,
        data: Any,
        type: Optional[str] = None,
        pattern: Optional[str] = None,
    ) -> NoReturn:
        self.topic: str = topic
        self.data: Any = data
        self.type: Optional[str] = type
        self.pattern: Optional[str] = pattern

    @property
    def __dict__(self) -> dict:
        return {
            'topic': self.topic,
            'data': self.data,
            'type': self.type,
            'pattern': self.pattern,
        }

    def __serialize__(self) -> str:
        assert is_valid_json(self.data), 'Message data must be valid JSON'
        return json.dumps(self.data)

    def __deserialize__(self) -> Any:
        return json.loads(self.data)

    @classmethod
    def deserialize(cls, data: dict) -> 'Message':
        return cls(data['topic'], data['data'])
