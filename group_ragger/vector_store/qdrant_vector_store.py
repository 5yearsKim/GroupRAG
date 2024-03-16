from typing import Any, Literal

from qdrant_client import QdrantClient 
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, PointIdsList, OrderBy, Direction

from .base import BaseVectorStore
from ..schema import Point, ScoredPoint, PointFactory



class QdrantVectorStore(BaseVectorStore):
    def __init__(self, qdrant_url: str='localhost:6333', namespace: str='test') -> None:
        self.namespace = namespace
        self.client = QdrantClient(
            url=qdrant_url
        )

    def get(self, id: int|str) -> Point:
        retrieved: list[Any] = self.client.retrieve(
            collection_name=self.namespace,
            ids=[id]
        )
        return PointFactory.from_qdrant(retrieved[0]) 

    def get_many(
        self,
        group_id: int|None=None,
        knowledge_id: int|None=None,
        limit:int=30,
        offset: str|None=None,
        with_vector:bool=False,
        order_by: Literal["asc", "desc"]|None=None,
    ) -> tuple[list[Point], str|None]:

        must_filter: list[Any] = []
        if group_id is not None:
            must_filter.append(FieldCondition(key='group_id', match=MatchValue(value=group_id)))
        if knowledge_id is not None:
            must_filter.append(FieldCondition(key='knowledge_id', match=MatchValue(value=knowledge_id)))

        fetched, next_cursor= self.client.scroll(
            collection_name=self.namespace,
            scroll_filter=Filter(
                must=must_filter
            ),
            with_vectors=with_vector,
            limit=limit,
            offset=offset,
            order_by=OrderBy(
                key='timestamp',
                direction=Direction.ASC if order_by == 'asc' else Direction.DESC,
            )
        )

        return [PointFactory.from_qdrant(point, with_vector=False) for point in fetched], next_cursor # type: ignore


    def upsert(self, point: Point) -> None:
        self.client.upsert(
            collection_name=self.namespace,
            points=[
                point.to_qdrant()
            ]
        )

    def upsert_many(self, points: list[Point]) -> None:
        self.client.upsert(
            collection_name=self.namespace,
            points=[
                point.to_qdrant() for point in points
            ]
        )

    def delete_many(self, ids: list[int|str]) -> None:
        self.client.delete(
            collection_name=self.namespace,
            points_selector=PointIdsList(points=ids)
        )
 
    def search(
        self,
        group_id: int,
        query_vector: list[float],
        limit: int=10,
        score_threshold: float=0.,
    ) -> list[ScoredPoint]:
        retrieved = self.client.search(
            collection_name=self.namespace,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=Filter(
                must=[
                    FieldCondition(key='group_id', match=MatchValue(value=group_id)),
                ]
            )
        )
        return [PointFactory.from_scored_qdrant(point) for point in retrieved]

    