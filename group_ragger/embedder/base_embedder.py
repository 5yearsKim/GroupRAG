from abc import ABC, abstractmethod

class BaseEmbedder(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def encode(self, texts: list[str]) -> list[list[float]] :
        raise NotImplementedError()
