import openai
from asyncio import sleep
import json
from typing import Iterable

class OpenAIGenerator:
    def __init__(self):
        self.o_client = openai.OpenAI()
        self.model = "gpt-3.5-turbo-0125"

    def _generate_stream(self, messages: list[dict]):
        stream = self.o_client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
        )
        return stream

    def generate(self, messages: list[dict]) -> Iterable[str]:
        stream = self._generate_stream(messages)

        async def response_streamer():
            text: str = ''

            for chunk in stream:
                # print(chunk.choices[0])
                finish_reason = chunk.choices[0].finish_reason
                content = chunk.choices[0].delta.content
                if content:
                    text += content
                wrapped = {
                    "chunk": chunk.choices[0].delta.content,
                    "text": text,
                    "status": "done" if finish_reason == "stop" else "progress"
                }
                await sleep(0.05)
                
                # yield text
                yield f"data: {json.dumps(wrapped, ensure_ascii=False)}"

        return response_streamer()