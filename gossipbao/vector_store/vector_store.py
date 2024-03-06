from qdrant_client import QdrantClient 
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, Distance, VectorParams, PointStruct
from ..schema import Point
from typing import Any



class VectorStore:
    def __init__(self, qdrant_url: str, namespace: str='test') -> None:
        self.namespace = namespace
        self.client = QdrantClient(
            url=qdrant_url
        )

    def upsert(self, point: Point) -> None:
        self.client.upsert(
            collection_name=self.namespace,
            points=[
                PointStruct(id=point.id, vector=point.vector, payload=point.payload) 
            ]
        )

    def upsert_many(self, points: list[Point]) -> None:
        self.client.upsert(
            collection_name=self.namespace,
            points=[
                PointStruct(id=point.id, vector=point.vector, payload=point.payload) 
                for point in points
            ]
        )
        

    def search(self, group_id: int, query_vector: list[float], limit: int=10, score_threshold: float=0.) -> list[Any]:
        return self.client.search(
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

    