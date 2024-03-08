from typing import Iterable
from fastapi import FastAPI
from pydantic import BaseModel
# from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sse_starlette.sse import EventSourceResponse


from group_ragger import GroupRagger
from group_ragger.vector_store import QdrantVectorStore
from group_ragger.embedder import OpenAIEmbedder
from group_ragger.rag_checker import OpenAIChecker
from group_ragger.generator import OpenAIGenerator
from group_ragger.schema import Group, Message, Point

from config import (
    OPENAI_API_KEY,
    QDRANT_URL, QDRANT_NAMESPACE, PORT
)


app = FastAPI()

embedder = OpenAIEmbedder(api_key=OPENAI_API_KEY)
generator = OpenAIGenerator(api_key=OPENAI_API_KEY)
vector_store = QdrantVectorStore(qdrant_url=QDRANT_URL, namespace=QDRANT_NAMESPACE)
checker = OpenAIChecker(api_key=OPENAI_API_KEY)


ragger = GroupRagger(
    generator=generator,
    embedder=embedder,
    vector_store=vector_store,
    checker=checker
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=100, add_start_index=True
)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "Healthy!"}

class CreateKnowledgeBody(BaseModel):
    id: int
    content: str
    group_id: int
    user_id: int

class CreateKnowledgeRsp(BaseModel):
    success: bool

@app.post('/knowledge', response_model=CreateKnowledgeRsp)
async def create_knowledge(body: CreateKnowledgeBody) -> CreateKnowledgeRsp:
    chunks = text_splitter.split_text(body.content)

    vectors = embedder.encode(chunks)

    points = [
        Point(
            id=Point.generate_id(),
            vector=vector,
            content=chunk,
            group_id=body.group_id,
        )
        for vector, chunk in zip(vectors, chunks)
    ]

    vector_store.upsert_many(points)

    return CreateKnowledgeRsp(success=True)


class RespondBody(BaseModel):
    group: Group
    user_id: int
    messages: list[Message]


@app.post('/bot/respond')
async def respond(body: RespondBody) -> EventSourceResponse:
    group, messages = body.group, body.messages

    stream = ragger.respond(messages, group)

    def response_streamer() -> Iterable[str]:
        for s_out in stream:
            yield f'data: {s_out.to_dict()}'

    return EventSourceResponse(response_streamer())



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT, reload=True, log_level="debug")
