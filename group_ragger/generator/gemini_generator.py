from typing import Iterable

import google.generativeai as genai

from .base import BaseGenerator
from ..schema import Message, StreamOutput


class GeminiGenerator(BaseGenerator):
    def __init__(self, api_key: str) -> None:
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')


    def _convert_messages_to_prompt(self, messages: list[Message]) -> str:
        prompt = '너는 아래 대화에서 bot의 역할을 해야해. 다음 대화에 이어질 적절한 답변을 해줘.\n\n'

        return prompt + '\n'.join([f'{m.role.name}: {m.content}' for m in messages])

    def generate_stream(self, messages: list[Message]) -> Iterable[StreamOutput]:

        prompt = self._convert_messages_to_prompt(messages)

        response_stream = self.model.generate_content(
            prompt,
            safety_settings={'HARASSMENT': 'block_none'},
            stream=True
        )
       
        def response_streamer() -> Iterable[StreamOutput]:
            text = ''
            for chunk in response_stream:
                text += chunk.text
                yield StreamOutput(
                    chunk=chunk.text,
                    text=text,
                    status= 'progress'
                )
            # end streamin
            yield StreamOutput(
                chunk='',
                text=text,
                status='done'
            )

        return response_streamer()
