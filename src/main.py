# import
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.vectorstores import Chroma


# create the open-source embedding function
embedding_fn = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


LOAD_FROM_DIR=True

if LOAD_FROM_DIR:
    db = Chroma(embedding_function=embedding_fn, persist_directory='./chroma_db')
    
else:
    # load the document and split it into chunks
    loader = TextLoader("./data/example.txt")
    documents = loader.load()

    # split it into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    # load it into Chroma
    db = Chroma.from_documents(docs, embedding_function=embedding_fn, persist_directory='./chroma_db')

# query it
query = "What is the first computer the author used?"
docs = db.similarity_search(query)

# print results
print(docs[0].page_content)