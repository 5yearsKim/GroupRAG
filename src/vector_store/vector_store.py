from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct


class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            host='localhost',
            port=6333
        )

    def upsert(self, id: int, vector: list[float], payload: dict={}, namespace: str='test'):
        self.client.upsert(
            collection_name=namespace,
            points=[
                PointStruct(id=id,vector=vector, payload=payload) 
            ]
        )

    def search(self, query_vector: list[float], namespace: str = 'test', limit: int =10):
        return self.client.search(
            collection_name=namespace,
            query_vector=query_vector,
            limit=limit
        )

    