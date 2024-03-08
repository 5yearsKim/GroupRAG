from pydantic import BaseModel
from qdrant_client.http.models import PointStruct as QdrantPoint, ScoredPoint as ScoredQdrantPoint
from typing import Any
import uuid


class Point(BaseModel):
    id: int|str
    vector: list[float]
    content: str 
    group_id: int|str
    meta: dict[str, Any]|None = None

    
    def __repr__(self) -> str:
        return f"Point(id={self.id}, content={self.content}, group_id={self.group_id})"

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    def to_qdrant(self) -> QdrantPoint:
        return QdrantPoint(
            id=self.id,
            vector=self.vector,
            payload={
                **(self.meta or {}) ,
                'content': self.content,
                'group_id': self.group_id,
            }
        )

class ScoredPoint(BaseModel):
    id: int|str
    content: str 
    group_id: int|str
    meta: dict[str, Any]|None = None
    score: float


class PointFactory:
    @staticmethod
    def from_qdrant(q_point: QdrantPoint, with_vector:bool=True) -> Point:
        payload: dict[str, Any] = q_point.payload # type: ignore
        return Point(
            id=q_point.id,
            vector=q_point.vector if with_vector else [], # type: ignore
            content=payload['content'],
            group_id=payload['group_id'],
            meta={k: v for k, v in payload.items() if k not in ['content', 'group_id']},
        )

    @staticmethod
    def from_scored_qdrant(q_point: ScoredQdrantPoint) -> ScoredPoint:
        payload: dict[str, Any] = q_point.payload # type: ignore
        return ScoredPoint(
            id=q_point.id,
            content=payload['content'],
            group_id=payload['group_id'],
            meta={k: v for k, v in payload.items() if k not in ['content', 'group_id']},
            score=q_point.score,
        )

    


