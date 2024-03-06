from pydantic import BaseModel


class Point(BaseModel):
    id: int
    vector: list[float]
    payload: dict = {}
    
    def __repr__(self) -> str:
        return f"Point(id={self.id})"
        