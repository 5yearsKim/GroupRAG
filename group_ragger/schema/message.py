from enum import Enum
from typing import Literal

from pydantic import BaseModel



class MessageRole(Enum):
    USER = 'user'
    BOT = 'bot'
    SYSTEM = 'system'
    FUNCTION = 'function'


class Message(BaseModel):
    role: MessageRole
    content: str

    def to_dict(self) -> dict[str, str]:
        return {'role': self.role.value, 'content': self.content}

    def to_openai(self) -> dict[str, str]:
        role = ''
        if self.role == MessageRole.USER:
            role = 'user'
        elif self.role == MessageRole.BOT:
            role = 'assistant'
        elif self.role == MessageRole.FUNCTION:
            role = 'function'
        elif self.role == MessageRole.SYSTEM:
            role = 'system'
        else:
            raise ValueError(f"Unsupported role: {self.role}")
        return {'role': role, 'content': self.content}

    def to_claude(self) -> dict[str, str]:
        role = ''
        if self.role == MessageRole.USER:
            role = 'user'
        elif self.role == MessageRole.BOT:
            role = 'assistant'
        elif self.role == MessageRole.FUNCTION:
            role = 'function'
        elif self.role == MessageRole.SYSTEM:
            role = 'system'
        else:
            raise ValueError(f"Unsupported role: {self.role}")
        return {'role': role, 'content': self.content}





class MessageFactory:
    @staticmethod
    def create_user_message(content: str) -> Message:
        return Message(role=MessageRole.USER, content=content)

    @staticmethod
    def create_bot_message(content: str) -> Message:
        return Message(role=MessageRole.BOT, content=content)

    @staticmethod
    def create_system_message(content: str) -> Message:
        return Message(role=MessageRole.SYSTEM, content=content)



class StreamOutput(BaseModel):
    chunk: str
    text: str
    status: Literal['done', 'progress']

    def to_dict(self) -> dict[str, str]:
        return {'chunk': self.chunk, 'text': self.text, 'status': self.status}

    


