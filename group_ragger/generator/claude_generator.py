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

    def _to_claude_message(self, messages: list[Message]) -> tuple[str, list[Message]]:
        '''
        returns: str(prompt), list[dict](claude_messages) 
        '''
        system_messages = list(filter(lambda m: m.role == MessageRole.SYSTEM, messages))
        system_prompt = '\n'.join([m.content for m in system_messages]) 

        claude_messages: list[Message] = []

        for msg in messages:
            if msg.role != MessageRole.USER and msg.role != MessageRole.BOT:
                continue
            if len(claude_messages) > 0 and claude_messages[-1].role == msg.role:
                claude_messages[-1].content += f' {msg.content}'
            else:
                claude_messages.append(msg)
        
        # first message should always be from user (https://docs.anthropic.com/claude/reference/messages_post)
        if len(claude_messages) == 0 or claude_messages[0].role != MessageRole.USER:
            claude_messages.insert(0, Message(role=MessageRole.USER, content="야"))
       
        return system_prompt, claude_messages



    def generate_stream(self, messages: list[Message]) -> Iterable[StreamOutput]:
        system_prompt, claude_msgs = self._to_claude_message(messages)

        text = ''
        # pylint: disable=not-context-manager
        with self.client.messages.stream(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            temperature=0.2,
            system=system_prompt,
            messages=[
                m.to_claude() for m in claude_msgs # type: ignore
            ]
        ) as stream_response: 
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
