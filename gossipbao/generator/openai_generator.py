import openai
from asyncio import sleep
from typing import Iterable, AsyncIterable, Any
from .base import BaseGenerator
from ..schema import Message, StreamOutput 

class OpenAIGenerator(BaseGenerator):
    def __init__(self) -> None:
        self.o_client = openai.OpenAI()
        self.model = "gpt-3.5-turbo-0125"


    def generate_stream(self, messages: list[Message]) -> AsyncIterable[StreamOutput]:
        stream: Any = self.o_client.chat.completions.create(
            model=self.model,
            messages=[m.to_openai() for m in messages], # type: ignore
            stream=True,
        )

        async def response_streamer() -> AsyncIterable[StreamOutput]:
            text: str = ''

            for chunk in stream:
                # print(chunk.choices[0])
                finish_reason = chunk.choices[0].finish_reason
                content = chunk.choices[0].delta.content
                if content:
                    text += content
                wrapped = StreamOutput(
                    chunk=chunk.choices[0].delta.content or '',
                    text=text,
                    status="done" if finish_reason == "stop" else "progress" 
                )
                await sleep(0.05)
                
                # yield text
                yield wrapped

        return response_streamer()