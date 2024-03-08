from abc import ABC, abstractmethod
from ..schema import Point, ScoredPoint
from typing import Any


class BaseVectorStore(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get(self, id: int|str) -> Point:
        raise NotImplementedError

    @abstractmethod
    def upsert(self, point: Point) -> None:
        raise NotImplementedError

    @abstractmethod
    def upsert_many(self, points: list[Point]) -> None:
        raise NotImplementedError


