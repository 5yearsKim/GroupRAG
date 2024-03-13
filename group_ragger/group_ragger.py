from typing import Iterable

from .rag_checker import OpenAIChecker
from .generator import BaseGenerator
from .embedder import BaseEmbedder
from .vector_store import BaseVectorStore
from .utils import cut_messages
from .schema import Group, Message, MessageRole, StreamOutput


class GroupRagger:
    def __init__(
        self,
        generator: BaseGenerator,
        embedder: BaseEmbedder ,
        vector_store: BaseVectorStore,
        checker: OpenAIChecker,
    ) -> None:
        self.generator = generator
        self.embedder = embedder
        self.vector_store = vector_store
        self.checker = checker

    def respond(self, messages: list[Message], group: Group) -> Iterable[StreamOutput]:
        """
        Get the messages from the user and respond to them with RAG
        """
        if len(messages) == 0:
            messages.append(
                Message(role=MessageRole.USER, content="안녕"),
            )

        short_end_messages = cut_messages(messages, max_len=300, max_turn=3)
        is_rag = self.checker.check_rag(short_end_messages)

        messages = cut_messages(messages, max_len=1000, max_turn=8)

        # print('messages:', messages)

        def get_query(messages: list[Message]) -> str:
            query = ''
            for msg in reversed(messages):
                if msg.role == MessageRole.USER:
                    query = f'{msg.content} {query}'
                else:
                    break
            return query

        if is_rag:

            query = get_query(messages)
            vectors = self.embedder.encode([query])

            retrieved = self.vector_store.search(group.id, vectors[0], limit=4, score_threshold=0.25)

            infos: list[str] = []
            for i, point in enumerate(retrieved):
                infos.append(f"{i + 1}. {point.content}")

            # print('infos: ', infos)

            guide = f"""
너의 이름은 '가십바오', 조직 '{group.name}'의 가십거리를 이야기 해주는 챗봇이야. 다음 원칙들을 지켜서 대답해줘.
1. 유저들에게는 인터넷 커뮤 말투를 써서 항상 반말로 대답해줘.
2. 유저가 물어보는 질문에는 다음 정보 중 한두가지 가장 정확한 정보를 기반으로 대답해줘. 질문에 해당하는 정보가 없으면 모른다고 대답해줘.
정보: {" / ".join(infos)}
3. 답변은 너무 길지 않고 핵심만 간결하게. (최대 60자)
            """

            messages.insert(0, Message(role=MessageRole.SYSTEM, content=guide))

            return self.generator.generate_stream(messages)
        else:
            prompt = """
너의 이름은 \'가십바오\', 가십거리를 이야기 해주는 챗봇이야. 다음 원칙들을 지켜서 대답해줘..
1. 유저들에게는 인터넷 커뮤 말투를 써서 항상 반말로 대답해줘.
2. 답변은 너무 길지 않게 간결하게.
            """
            messages.insert(0, Message(role=MessageRole.SYSTEM, content=prompt))
            return self.generator.generate_stream(messages)

    def trigger(self, messages: list[Message], group: Group) -> Iterable[StreamOutput]:
        """
        Start a new chat given the messages
        """
        prompt = """
너의 이름은 \'가십바오\', 가십거리를 이야기 해주는 챗봇이야.
다음 원칙을 지켜줘.
1. 유저들에게는 인터넷 커뮤 말투를 써서 항상 반말로 대답해줘.
2. 문맥을 고려하되 유저와의 대화를 새로 시작해줘.
        """
        messages.insert(0, Message(role=MessageRole.SYSTEM, content=prompt))
        return self.generator.generate_stream(messages)


