from pydantic import BaseModel


class RetrievalInput(BaseModel):
    should_retrieve: bool
    query: str=''
