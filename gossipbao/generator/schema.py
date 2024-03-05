from pydantic import BaseModel
from enum import Enum



class MessageRole(Enum):
    USER = 1
    BOT = 2
    SYSTEM = 3


class Message(BaseModel):
    role: MessageRole
    content: str

    @classmethod
    def from_dict(cls, d: dict) -> Message:
        return cls(role=MessageRole[d['role']], content=d['content'])

    def to_dict(self) -> dict[str, str]:
        return {'role': self.role.name, 'content': self.content}


