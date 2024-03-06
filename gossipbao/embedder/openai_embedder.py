import openai
from .base_embedder import BaseEmbedder


class OpenAIEmbedder(BaseEmbedder):
    def __init__(self) -> None:
        super().__init__()
        self.o_client = openai.OpenAI()
        self.model = "text-embedding-3-small"


    def encode(self, texts: list[str]) -> list[list[float]] :
        rsp = self.o_client.embeddings.create(
            input=texts,
            model=self.model
        )

        return list(map(lambda x: x.embedding, rsp.data))


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    embedder = OpenAIEmbedder()
    vectors = embedder.encode(["hello", "world"])

    print(len(vectors[0])) # 1536