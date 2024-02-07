# import
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.vectorstores import Chroma
import uuid
import chromadb



# create the open-source embedding function
embedding_fn = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

client = chromadb.HttpClient(
    host='localhost',
    port=8080,
    settings=chromadb.config.Settings(
        allow_reset=True,
        is_persistent=True,
    )
)
# client.reset()  # resets the database

collection = client.get_or_create_collection("my_collection")

# load the document and split it into chunks
loader = TextLoader("./data/example.txt")
documents = loader.load()

# split it into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

for doc in docs:
    collection.add(
        ids=[str(uuid.uuid1())], metadatas=doc.metadata, documents=doc.page_content
    )

# tell LangChain to use our client and collection name
db = Chroma(
    client=client,
    collection_name="my_collection",
    embedding_function=embedding_fn,
)


query = "What did the president say about Ketanji Brown Jackson"
docs = db.similarity_search(query)
print(docs[0].page_content)





# # db.add_texts(['hyunwoo is a handsome boy'], namespace='test')

# # query it
# query = "who is hyunwoo?"
# docs = db.similarity_search(query)

# # print results
# print(docs[0])