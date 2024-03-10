from abc import ABC
from typing import Iterable

from ..schema import Message, StreamOutput

class BaseGenerator(ABC):
    def __init__(self) -> None:
        pass

    def generate_stream(self, messages: list[Message]) -> Iterable[StreamOutput]:
        raise NotImplementedError