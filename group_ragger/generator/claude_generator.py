""" cloude generator """
from typing import Iterable
import anthropic
from .base import BaseGenerator
from ..schema import Message, StreamOutput, MessageRole


class ClaudeGenerator(BaseGenerator):
    def __init__(self, api_key: str) -> None:
        self.client = anthropic.Anthropic(
            api_key=api_key,
        )


    def generate_stream(self, messages: list[Message]) -> Iterable[StreamOutput]:
        system_messages = list(filter(lambda m: m.role == MessageRole.SYSTEM, messages))

        system_prompt = '\n'.join([m.content for m in system_messages]) 

        non_system_messages = list(filter(lambda m: m.role != MessageRole.SYSTEM, messages))
        

        text = ''
        stream_response = self.client.messages.stream(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            temperature=0.2,
            system=system_prompt,
            messages=[
                m.to_claude() for m in non_system_messages # type: ignore
            ]
        )

        for chunk in stream_response.text_stream:
            text += chunk
            yield StreamOutput(
                chunk=chunk,
                text=text,
                status="progress"
            )
        yield StreamOutput(
            chunk='',
            text=text,
            status="done"
        )
