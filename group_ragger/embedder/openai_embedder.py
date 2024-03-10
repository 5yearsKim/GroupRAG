import openai
from .base_embedder import BaseEmbedder


class OpenAIEmbedder(BaseEmbedder):
    def __init__(self, api_key: str) -> None:
        super().__init__()
        self.o_client = openai.OpenAI(api_key=api_key)
        self.model = "text-embedding-3-small"


    def encode(self, texts: list[str]) -> list[list[float]] :
        rsp = self.o_client.embeddings.create(
            input=texts,
            model=self.model
        )

        return list(map(lambda x: x.embedding, rsp.data))
