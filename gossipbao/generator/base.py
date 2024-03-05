from abc import ABC
from .schema import Message


class BaseGenerator(ABC):
    def __init__(self) -> None:
        pass

    def generate(self, Message):
        raise NotImplementedError