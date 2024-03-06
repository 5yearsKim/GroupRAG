from abc import ABC
from ..schema import Message, StreamOutput 
from typing import AsyncIterable



class BaseGenerator(ABC):
    def __init__(self) -> None:
        pass

    def generate_stream(self, messages: list[Message]) -> AsyncIterable[StreamOutput]:
        raise NotImplementedError