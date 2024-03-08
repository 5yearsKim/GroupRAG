from typing import AsyncIterable, Literal

from .rag_checker import OpenAIChecker
from .generator import BaseGenerator
from .embedder import BaseEmbedder
from .vector_store import QdrantVectorStore
from .utils import cut_messages
from .schema import Group, Message, MessageRole, StreamOutput 

GeneratorCand = Literal['openai', 'gemini', 'claude']

class GroupRagger:
    def __init__(
        self,
        generator: BaseGenerator,
        embedder: BaseEmbedder ,
        vector_store: QdrantVectorStore,
        checker: OpenAIChecker,
    ) -> None:
        self.generator = generator
        self.embedder = embedder
        self.vector_store = vector_store
        self.checker = checker

    def respond(self, messages: list[Message], group: Group) -> AsyncIterable[StreamOutput]:
        if len(messages) == 0:
            messages.append(
                Message(role=MessageRole.USER, content="안녕"),
            )

        short_end_messages = cut_messages(messages, max_len=300, max_turn=3)
        is_rag = self.checker.check_rag(short_end_messages)

        messages = cut_messages(messages, max_len=1000, max_turn=8)

        # print('messages:', messages)

        if is_rag:
            query = messages[-1].content
            vectors = self.embedder.encode([query])

            retrieved = self.vector_store.search(group.id, vectors[0], limit=4, score_threshold=0.25)

            infos: list[str] = []
            for i, point in enumerate(retrieved):
                infos.append(f"{i + 1}. {point.content}")

            guide = f"""
            너의 이름은 '가십바오', 조직 '{group.name}'의 가십거리를 이야기 해주는 챗봇이야. 유저들에게는 항상 반말로 대답해주되 구어체로 대답해줘. ~다. 로 끝나는 말투는 금지.
            유저가 물어보는 질문에는 다음 정보 중 한두가지 가장 정확한 정보를 기반으로 대답해줘. 정보가 없으면 모른다고 대답해줘. 답변은 50자를 넘지 않게 간결하게.

            정보: {" / ".join(infos)}
            """

            messages.insert(0, Message(role=MessageRole.SYSTEM, content=guide))

            return self.generator.generate_stream(messages)
        else:
            prompt = "너의 이름은 \'가십바오\', 가십거리를 이야기 해주는 챗봇이야. 유저들에게는 항상 반말로 대답해줘."
            messages.insert(0, Message(role=MessageRole.SYSTEM, content=prompt))
            return self.generator.generate_stream(messages)

