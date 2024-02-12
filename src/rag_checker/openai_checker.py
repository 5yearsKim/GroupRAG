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



if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    checker = OpenAIChecker()
    messages = [
        {"role": "assistant", "content": "가십바오 alskfnasdlkfn;sfknsf;la ns;flaksnd falksd nflknf lsknflsdknflskn"},
        {"role": "user", "content": "안녕하세요."},
        {"role": "assistant", "content": "안녕."},
        # {"role": "user", "content": "어제 뭐했어"},
        {"role": "user", "content": "심심하다"},
    ]
    is_rag = checker.check_rag(messages)

    print(is_rag)