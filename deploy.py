from config import QDRANT_URL, QDRANT_NAMESPACE, PORT
from typing import Union, Literal, AsyncIterable
from fastapi import FastAPI
from fastapi.responses import StreamingResponse 
from pydantic import BaseModel
# from sentence_transformers import SentenceTransformer
import uuid


from langchain.text_splitter import RecursiveCharacterTextSplitter
from embedder import OpenAIEmbedder
from rag_checker import OpenAIChecker
from generator import OpenAIGenerator
from gossipbao import GossipBao
from gossipbao.schema import Group, Message, MessageRole, Point
from sse_starlette.sse import EventSourceResponse
from utils import cut_messages

app = FastAPI()


bao = GossipBao(generator_type='openai')

vector_store = bao.vector_store
# embedding_fn = SentenceTransformer('all-MiniLM-L6-v2')
# embedding_fn = SentenceTransformer('jhgan/ko-sroberta-multitask')
embedder = bao.embedder

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

    points: list[Point] = []
    for i, (vector, chunk) in enumerate(zip(vectors, chunks)):
        point_id = str(uuid.uuid4())
        payload = {"knowledge_id": body.id, "user_id": body.user_id, "group_id": body.group_id, "content": chunk}
        point = Point(id=point_id, vector=vector, payload=payload)
        points.append(point)

    vector_store.upsert_many(points)

    return CreateKnowledgeRsp(success=True)


class CreateContextBody(BaseModel):
    id: int
    context: str
    group_id: int

class CreateContextRsp(BaseModel):
    id: int
    context: str


@app.post('/contexts', response_model=CreateContextRsp)
async def create_context(body: CreateContextBody) -> CreateContextRsp:
    embedded = embedder.encode([body.context])
    vector_store.upsert(id=body.id, vector=embedded)
    return CreateContextRsp(id=body.id, context=body.context)


class RespondBody(BaseModel):
    group: Group 
    user_id: int
    messages: list[Message]



@app.post('/bot/respond')
async def respond(body: RespondBody) -> EventSourceResponse:
    group = body.group
    messages = body.messages

    short_end_messages = cut_messages(messages, max_len=300, max_turn=3)

    stream = bao.respond(short_end_messages, group)

    async def response_streamer() -> AsyncIterable[str]:
        async for s_out in stream:
            yield f'data: {s_out}' 

    return EventSourceResponse(response_streamer) # type: ignore




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT, reload=True, log_level="debug")
'''
prod:
uvicorn deploy:app --host=0.0.0.0 --port=8010

dev:
uvicorn deploy:app --host=0.0.0.0 --port=8020 --log-level=debug --reload
'''