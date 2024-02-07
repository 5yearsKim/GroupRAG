from dotenv import load_dotenv
load_dotenv()

from typing import Union
import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from vector_store import VectorStore
from sentence_transformers import SentenceTransformer
from sse_starlette.sse import EventSourceResponse
from openai import OpenAI
from asyncio import sleep
import json

app = FastAPI()

vector_store = VectorStore()
# embedding_fn = SentenceTransformer('all-MiniLM-L6-v2')
embedding_fn = SentenceTransformer('jhgan/ko-sroberta-multitask')

o_client = OpenAI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


class CreateContextBody(BaseModel):
    id: int
    context: str


@app.post('/contexts')
async def create_context(body: CreateContextBody):
    embedded = embedding_fn.encode(body.context)
    vector_store.upsert(id=body.id, vector=embedded)
    return {"id": body.id, "context": body.context}


@app.post('/bot/check-rag')
async def check_rag():
    pass


class RespondBody(BaseModel):
    query: str

class ResponseRsp(BaseModel):
    response: str



@app.post('/bot/respond')
async def respond(body: RespondBody, response_model=ResponseRsp):
    embedded = embedding_fn.encode(body.query)

    fetched = vector_store.search(query_vector=embedded)
    print(fetched)

    return {"response": "Hello World"}

class GenerateBody(BaseModel):
    context: str



@app.post('/bot/generate')
async def generate(body: GenerateBody):

    stream= o_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
        ],
        stream=True,
    )

    async def response_streamer():
        text: str = ''

        for chunk in stream:
            print(chunk.choices[0])
            finish_reason = chunk.choices[0].finish_reason
            content = chunk.choices[0].delta.content
            if content:
                text += content
            wrapped = {
                "content": chunk.choices[0].delta.content,
                "text": text,
                "status": "done" if finish_reason == "stop" else "progress"
            }
            # await sleep(0.2)

            yield f"data: f{json.dumps(wrapped)}\n\n".encode('utf-8')


    return EventSourceResponse(response_streamer())


@app.get('/test-stream')
async def test_stream():
    async def response_streamer():
        for i in range(10):
            print(i)
            # yield json.dumps({"content": f"hello world {i}"}).encode('utf-8')
            yield 'data: hello'

            await sleep(0.2)
    return EventSourceResponse(response_streamer())    



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010, reload=True, log_level="debug")
'''
uvicorn deploy:app --host=0.0.0.0 --port=8010 --log-level=debug --reload
'''