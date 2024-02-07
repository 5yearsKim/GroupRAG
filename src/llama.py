from dotenv import load_dotenv 
load_dotenv()

# from langchain_openai import ChatOpenAI

# llm = ChatOpenAI(model_name='gpt-3.5-turbo')

# val = llm.invoke("how can langsmith help with testing?")

# print(val)



# from openai import OpenAI


# client = OpenAI()


# stream = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[{"role": "user", "content": "안녕. 너가 누군지 소개해줄래?"}],
#     stream=True,
# )

# print('stream: ',stream)
# for chunk in stream:
#     content = chunk.choices[0].delta.content
#     if content is not None:
#         print(content)


import os.path
from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

PERSIST_DIR = "./storage"
if not os.path.exists(PERSIST_DIR):
    # load the documents and create the index
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    # store it for later
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    # load the existing index
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)


query_engine = index.as_query_engine()

retrieved = query_engine.retrieve("What did the author do growing up?")
print(retrieved)

# response = query_engine.query("What did the author do growing up?")
# print(response)
