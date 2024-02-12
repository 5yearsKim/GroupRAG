from dotenv import load_dotenv
load_dotenv()

from typing import Union, Literal
import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
# from sentence_transformers import SentenceTransformer
import uuid


from langchain.text_splitter import RecursiveCharacterTextSplitter
from vector_store import VectorStore, Point
from embedder import OpenAIEmbedder
from rag_checker import OpenAIChecker
from generator import OpenAIGenerator
from sse_starlette.sse import EventSourceResponse
from utils import cut_messages

app = FastAPI()

vector_store = VectorStore(namespace='gossip_dev')
# embedding_fn = SentenceTransformer('all-MiniLM-L6-v2')
# embedding_fn = SentenceTransformer('jhgan/ko-sroberta-multitask')
embedder = OpenAIEmbedder()
checker = OpenAIChecker()
generator = OpenAIGenerator()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=100, add_start_index=True
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


class CreateKnowledgeBody(BaseModel):
    id: int
    content: str
    group_id: int
    user_id: int

@app.post('/knowledge')
async def create_knowledge(body: CreateKnowledgeBody):
    chunks = text_splitter.split_text(body.content)

    vectors= embedder.encode(chunks)

    points: list[Point] = []
    for i, (vector, chunk) in enumerate(zip(vectors, chunks)):
        point_id = str(uuid.uuid4())
        payload = {"knowledge_id": body.id, "user_id": body.user_id, "group_id": body.group_id, "content": chunk}
        point = Point(id=point_id, vector=vector, payload=payload)
        points.append(point)

    return vector_store.upsert_many(points)


class CreateContextBody(BaseModel):
    id: int
    context: str
    group_id: int


@app.post('/contexts')
async def create_context(body: CreateContextBody):
    embedded = embedding_fn.encode(body.context)
    vector_store.upsert(id=body.id, vector=embedded)
    return {"id": body.id, "context": body.context}


class MessageT(BaseModel):
    role: Literal['user', 'bot', 'system']
    content: str

def message_to_dict(message: MessageT):
    role: str = message.role
    if role == 'bot':
        role = 'assistant'
    content = message.content
    return {"role": role, "content": content}

class RespondBody(BaseModel):
    group_id: int
    user_id: int
    messages: list[MessageT]


@app.post('/bot/respond')
async def respond(body: RespondBody):

    messages = list(map(message_to_dict, body.messages))

    if len(messages) == 0:
        messages.append({"role": "user", "content": "안녕"})

    short_end_messages = cut_messages(messages, max_len=300, max_turn=3)
    is_rag = checker.check_rag(short_end_messages)

    messages = cut_messages(messages, max_len=1000, max_turn=8)

    # print('messages:', messages)

    if is_rag:
        query = messages[-1]['content']
        vectors = embedder.encode([query])

        retrieved = vector_store.search(body.group_id, vectors[0], limit=3, score_threshold=0.25)

        infos: list[str] = []
        for i, point in enumerate(retrieved):
            infos.append(f"{i + 1}. {point.payload['content']}")

        guide = f"""
        너의 이름은 '가십바오', 가십거리를 이야기 해주는 챗봇이야. 유저들에게는 항상 반말로 대답해주되 구어체로 대답해줘. ~다. 로 끝나는 말투는 금지.
        유저가 물어보는 질문에는 다음 정보를 기반으로 대답해줘. 정보가 없으면 모른다고 대답해줘. 답변은 50자를 넘지 않게 간결하게.

        정보: {" / ".join(infos)}
        """

        messages.insert(0, {"role": "system", "content": guide})

        response_streamer = generator.generate(messages)
        return EventSourceResponse(response_streamer)
    else:
        messages.insert(0, {"role": "system", "content": "너의 이름은 \'가십바오\', 가십거리를 이야기 해주는 챗봇이야. 유저들에게는 항상 반말로 대답해줘."})
        response_streamer = generator.generate(messages)
        return EventSourceResponse(response_streamer)


class GenerateBody(BaseModel):
    messages: list[MessageT]

@app.post('/bot/generate')
async def generate(body: GenerateBody):
    messages = list(map(message_to_dict, body.messages))
    
    messages.append({"role": "system", "content": "반말로 대답해줘."})

    response_streamer = generator.generate(messages)

    return EventSourceResponse(response_streamer)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010, reload=True, log_level="debug")
'''
uvicorn deploy:app --host=0.0.0.0 --port=8010 --log-level=debug --reload
'''