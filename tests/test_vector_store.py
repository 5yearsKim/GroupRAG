from test_utils import set_python_path
set_python_path()

from group_ragger.vector_store import QdrantVectorStore
from group_ragger.embedder import OpenAIEmbedder
from config import QDRANT_URL, QDRANT_NAMESPACE, OPENAI_API_KEY
from group_ragger.schema import Point

store = QdrantVectorStore(
    namespace=QDRANT_NAMESPACE,
    qdrant_url=QDRANT_URL,
)
embedder = OpenAIEmbedder(
    api_key=OPENAI_API_KEY
)

def test_get() -> None:
    vector = store.get("05ca5c45-8a10-494a-88b1-a68196a84667")
    print(vector)

def test_upsert() -> None:
    sent = '내 이름은 onion이야'
    vector = embedder.encode([sent])[0]
    point = Point(
        id=Point.generate_id(),
        vector=vector,
        group_id=1,
        content=sent
    )
    store.upsert(point)


def test_search() -> None:
    sent = '오원주에 대해 알려줘.'
    vector = embedder.encode([sent])[0]
    found = store.search(group_id=3, query_vector=vector)
    print(found)

def test_get_many() -> None:
    points = store.get_many(group_id=1, knowledge_id=32)
    print(points)



if __name__ == "__main__":
    # test_fetch()
    # test_upsert()
    # test_search()
    test_get_many()
