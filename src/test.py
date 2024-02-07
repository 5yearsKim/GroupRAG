# import
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
# from langchain_community.embeddings.sentence_transformer import (
#     SentenceTransformerEmbeddings,
# )
from langchain_community.vectorstores import Chroma
import uuid
import chromadb
from chromadb.utils import embedding_functions




# embedding_fn = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

client = chromadb.HttpClient(
    host='localhost',
    port=8080,
    settings=chromadb.config.Settings(
        allow_reset=True,
        is_persistent=True,
    )
)

collection = client.get_or_create_collection("my_collection", embedding_function=embedding_fn)


collection.add(
    documents=['hyunwoo is the hansome boy'],
    ids=['hyunwoo'],
    metadatas=[{'group': 'hyunwoo'}]
)

results = collection.query(
    query_texts=['who is hyunwoo?'],
    where={"group": "hyunwoo"},
    n_results=2,
)

print(results)


