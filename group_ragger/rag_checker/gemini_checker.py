from typing import Iterable

import google.generativeai as genai

from .base import BaseRagChecker 
from ..schema import Message, RetrievalInput 


class GeminiChecker(BaseRagChecker):
    def __init__(self, api_key: str) -> None:
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')


    def _convert_messages_to_prompt(self, messages: list[Message]) -> str:
        prompt = """
 다음 대화에 따라 AI 어시스턴트가 대답을 해줘야 하는데 RAG(Retrieval) 를 해야 하는지 json 으로 결과를 알려줘.
답변은 json 으로 다음 형식과 같아야 해.
json 형식: {
should_retrieve: boolean, // 마지막 유저 발화가 정보를 묻는 질문이라면 RAG 를 해야하므로 true, 아니라면 false
query?: string  // should_retrieve 가 false 면 query 는 없어도 되고, true 면 retrieve 할 때 필요한 키워드를 적어줘.
}

그럼 대화를 참조해서 RAG 를 해야하는지 알려줘.

"""

        return prompt + '\n'.join([f'{m.role.name}: {m.content}' for m in messages])



    def check_rag(self, messages: list[Message]) -> RetrievalInput:

        prompt = self._convert_messages_to_prompt(messages)


        rsp = self.model.generate_content(prompt,
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                temperature=0.0,
            )
        )
 
        return self.parse_response(rsp.text) # type: ignore
