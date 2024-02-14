from qdrant_client import QdrantClient 
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, Distance, VectorParams, PointStruct

class Point:
    def __init__(self, id: int|str, vector: list[float], payload: dict={}):
        self.id = id
        self.vector = vector
        self.payload = payload
    
    def __repr__(self):
        return f"Point(id={self.id})"


class VectorStore:
    def __init__(self, qdrant_url, namespace: str='test'):
        self.namespace = namespace
        self.client = QdrantClient(
            url=qdrant_url
        )

    def upsert(self, point: Point):
        return self.client.upsert(
            collection_name=self.namespace,
            points=[
                PointStruct(id=point.id, vector=point.vector, payload=point.payload) 
            ]
        )

    def upsert_many(self, points: list[Point]):
        return self.client.upsert(
            collection_name=self.namespace,
            points=[
                PointStruct(id=point.id, vector=point.vector, payload=point.payload) 
                for point in points
            ]
        )
        

    def search(self, group_id, query_vector: list[float], limit: int =10, score_threshold: float=0.):
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

    