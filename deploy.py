from typing import AsyncIterable, Literal
import json
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
# from sentence_transformers import SentenceTransformer
from sse_starlette.sse import EventSourceResponse


from group_ragger import GroupRagger
from group_ragger.vector_store import QdrantVectorStore
from group_ragger.embedder import OpenAIEmbedder
from group_ragger.rag_checker import OpenAIChecker
from group_ragger.generator import BaseGenerator, OpenAIGenerator, ClaudeGenerator, GeminiGenerator
from group_ragger.schema import Group, Message, Point

from config import (
    STAGE,
    OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY,
    QDRANT_URL, QDRANT_NAMESPACE, PORT
)


app = FastAPI()

embedder = OpenAIEmbedder(api_key=OPENAI_API_KEY)
vector_store = QdrantVectorStore(qdrant_url=QDRANT_URL, namespace=QDRANT_NAMESPACE)
checker = OpenAIChecker(api_key=OPENAI_API_KEY)

openai_generator = OpenAIGenerator(api_key=OPENAI_API_KEY)
claude_generator = ClaudeGenerator(api_key=ANTHROPIC_API_KEY)
gemini_generator = GeminiGenerator(api_key=GOOGLE_API_KEY)

GeneratorT = Literal["openai", "claude", "gemini"]

def get_generator(generator_type: GeneratorT|None) -> BaseGenerator|None:
    if generator_type == "openai":
        return openai_generator
    if generator_type == "claude":
        return claude_generator
    if generator_type == "gemini":
        return gemini_generator
    return None

ragger = GroupRagger(
    generator=claude_generator,
    embedder=embedder,
    vector_store=vector_store,
    checker=checker,
    verbose=(STAGE=="dev"),
)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "Healthy!"}

class ListKnowledgeRsp(BaseModel):
    points: list[Point]
    next_cursor: str|None

@app.get('/knowledge', response_model=ListKnowledgeRsp)
async def get_knowledge(group_id: int|None=None, cursor: str|None=None ) -> ListKnowledgeRsp:
    retrieved, next_cursor = ragger.vector_store.get_many(group_id=group_id, offset=cursor)
    return ListKnowledgeRsp(points=retrieved, next_cursor=next_cursor)


class CreateKnowledgeBody(BaseModel):
    id: int|None=None
    content: str
    group_id: int
    user_id: int|None=None

class CreateKnowledgeRsp(BaseModel):
    success: bool
    points: list[Point]


@app.post('/knowledge', response_model=CreateKnowledgeRsp)
async def create_knowledge(body: CreateKnowledgeBody) -> CreateKnowledgeRsp:

    points = ragger.memorize(body.content, body.group_id, user_id=body.user_id, knowledge_id=body.id)

    return CreateKnowledgeRsp(success=True, points=points)


class DeleteKnowledgeRsp(BaseModel):
    success: bool
    points: list[Point]

@app.delete('/knowledge/{knowledge_id}', response_model=DeleteKnowledgeRsp)
async def delete_knowledge(knowledge_id: int) -> DeleteKnowledgeRsp:
    points = ragger.forget(knowledge_id)
    return DeleteKnowledgeRsp(success=True, points=points)


class RespondBody(BaseModel):
    group: Group
    user_id: int
    messages: list[Message]
    generator_type: GeneratorT|None=None


@app.post('/bot/respond')
async def respond(body: RespondBody) -> EventSourceResponse:
    group, messages, generator_type = \
        body.group, body.messages, body.generator_type

    generator: BaseGenerator|None = get_generator(generator_type)

    stream = ragger.respond(messages, group, generator=generator)

    async def response_streamer() -> AsyncIterable[str]:
        for s_out in stream:
            yield f'data: {json.dumps(s_out.to_dict(), ensure_ascii=False)}'

    return EventSourceResponse(response_streamer())
    # return StreamingResponse(response_streamer(), headers={'Content-Type': 'text/event-stream'})


class TriggerBody(BaseModel):
    group: Group
    user_id: int
    messages: list[Message]
    generator_type: GeneratorT|None=None


@app.post('/bot/trigger')
async def trigger(body: TriggerBody) -> EventSourceResponse:
    group, messages, generator_type = \
        body.group, body.messages, body.generator_type

    generator: BaseGenerator|None = get_generator(generator_type)

    stream = ragger.trigger(messages, group, generator=generator)

    async def response_streamer() -> AsyncIterable[str]:
        for s_out in stream:
            yield f'data: {json.dumps(s_out.to_dict(), ensure_ascii=False)}'

    return EventSourceResponse(response_streamer())
    # return StreamingResponse(response_streamer(), headers={'Content-Type': 'text/event-stream'})


@app.get('/test-stream')
async def stream_test() -> StreamingResponse:
    async def response_streamer() -> AsyncIterable[str]:
        for i in range(30):
            yield f'data: {json.dumps({"i": i})}'
            await asyncio.sleep(0.5)

    return StreamingResponse(response_streamer(),\
         headers={'Content-Type': 'text/event-stream'})



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT, reload=True, log_level="debug")
