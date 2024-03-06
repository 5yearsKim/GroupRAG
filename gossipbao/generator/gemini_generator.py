
import google.generativeai as genai
from ..config import GOOGLE_API_KEY
from typing import AsyncIterable
from .base import BaseGenerator
from ..schema import Message, StreamOutput 


class GeminiGenerator(BaseGenerator):
    def __init__(self) -> None:
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')


    def _convert_messages_to_prompt(self, messages: list[Message]) -> str:
        prompt = '너는 아래 대화에서 bot의 역할을 해야해. 다음 대화에 이어질 적절한 답변을 해줘.\n\n'

        return prompt + '\n'.join([f'{m.role.name}: {m.content}' for m in messages])

    def generate_stream(self, messages: list[Message]) -> AsyncIterable[StreamOutput]:

        prompt = self._convert_messages_to_prompt(messages)

        response_stream = self.model.generate_content(prompt, stream=True)
        
        async def response_streamer() -> AsyncIterable[StreamOutput]:
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

