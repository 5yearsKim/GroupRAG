from qdrant_client import QdrantClient 
from qdrant_client.http.models import Distance, VectorParams

client = QdrantClient(
    host='localhost',
    port=6333
)

client.create_collection(
    collection_name='test',
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
)

