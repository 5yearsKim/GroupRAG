import openai


class OpenAIChecker:
    def __init__(self, max_len: int = 300, max_turn: int=3):
        self.o_client = openai.OpenAI()
        self.max_len = max_len
        self.max_turn = max_turn
    
    def check_rag(self, messages: list[dict]) -> bool:
        new_messages = messages.copy()
        system_message = {
            "role": "system",
            "content": """마지막 유저의 말이 정보를 묻는 질문이야? 여부를 O, X 로 대답해줘."""
        }
        new_messages.append(system_message)

        rsp = self.o_client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=new_messages,
            stream=False,
            temperature=0.
        )
        return rsp.choices[0].message.content == "O"

    def check_action(self, messages: list[dict]):
        prompt = '\n'.join([
            f'대화: {str(messages)}', 
            '위 대화를 참조해서 어떤 Commands 를 사용해야 하는지 골라줘. 너의 역할은 사용자와 대화하면서 정보를 기억하고, 필요한 정보를 찾아서 대답해줄 수 있어.',
            '답변을 해주는 게 아니라 다음 중 하나의 액션을 취할 수 있어. 액션을 선택해줘.',
'''
## Constraints
You operate within the following constraints:
1. Exclusively use the commands listed below.
2. The response should be Typescript object for Params.
3. "guide" in Params is optional and used for guideline to generate response.
''',
'''
## Commands
1. answer: 다른 액션 없이 답변을 생성. 일상적인 대화에 적합. Params: { guide?: string }
2. save_info: 사용자의 발언에서 인명이나 지명 등 구체적으로 기억해야 할 정보들이 있으면 요약해서 저장.  Params: { infos: string[], guide?: string  }
3. retrieve: 저장했던 정보들을 찾아서 기반으로 대답해줘야 할 때 정보를 찾아옴. 구체적인 정보를 묻는 질문에 적합. Params: { query: string, guide?: string }
''',
'''
## Example
1. user: "오늘 기분이 어때?" -> { "command": "answer", "guide": "오늘의 활기찬 기분을 묘사해줘." }
2. user: "최OO는 돈을 뺐는 매우 나쁜 사람이야. 또 여자친구가 있는 것 같아." -> { "command": "save_info", "infos": ["최OO는 돈을 뺐는 매우 나쁜 사람이다.", "최OO는 여자친구가 있다."], "guide": "잘 기억해두겠다는 말을 해줘." }
3. user: "김OO에 대해서 아는거 있어?" -> { "command": "retrieve", "query": "김OO", "guide": "김OO에 대한 정보를 찾아서 대답해줘. 없으면 유저에게 정보를 물어봐줘." }
'''

        ])

        print(prompt)
        new_messages = messages.copy()
        # new_messages = []
        system_message = {
            "role": "system",
            "content": prompt
        }
        new_messages.append(system_message)


        rsp = self.o_client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=new_messages,
            stream=False,
            temperature=0.
        )

        return rsp.choices[0].message







if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    checker = OpenAIChecker()
    messages = [
        {"role": "assistant", "content": "가십바오 alskfnasdlkfn;sfknsf;la ns;flaksnd falksd nflknf lsknflsdknflskn"},
        {"role": "user", "content": "안녕하세요."},
        {"role": "assistant", "content": "안녕."},
        # {"role": "user", "content": "어제 뭐했어"},
        {"role": "user", "content": "김현우는 코딩을 진짜 잘하는 사람이래. "},
    ]
    action = checker.check_action(messages)

    print(action)