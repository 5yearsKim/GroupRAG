from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient 
from qdrant_client.http.models import Distance, VectorParams
import os

qdrant_url = os.getenv('QDRANT_URL')

client = QdrantClient(
    url=qdrant_url,
)


print('qdrant host: ', qdrant_url)

# client.create_collection(
#     collection_name='test',
#     vectors_config=VectorParams(size=768, distance=Distance.COSINE)
#  )



client.create_collection(
    collection_name='gossip_prod',
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)

