from test_utils import set_python_path
set_python_path()

from group_ragger.rag_checker import OpenAIChecker, GeminiChecker
from group_ragger.schema import Message, MessageRole
from config import OPENAI_API_KEY, GOOGLE_API_KEY



test_sets: list[list[Message]] = [
    [
        Message(role=MessageRole.USER, content="안녕"),
        Message(role=MessageRole.BOT, content="무슨 이야기 해줄까?"),
        Message(role=MessageRole.USER, content="김현탁에 대해서 알려줘"),
    ],
    [
        Message(role=MessageRole.USER, content="안녕"),
        Message(role=MessageRole.BOT, content="무슨 이야기 해줄까?"),
        Message(role=MessageRole.USER, content="오늘 날씨 너무 좋네~"),
    ],
    [
        Message(role=MessageRole.USER, content="안녕"),
        Message(role=MessageRole.BOT, content="무슨 이야기 해줄까?"),
        Message(role=MessageRole.USER, content="오노마에이아이는 무슨 회사야?"),
        Message(role=MessageRole.BOT, content="웹툰을 만드는 AI 스타트업이야."),
        Message(role=MessageRole.USER, content="무슨 웹툰을 만드는데?"),

    ],
]


def test_openai_checker() -> None:
    checker = OpenAIChecker(api_key=OPENAI_API_KEY)

    for msgs in test_sets:
        result = checker.check_rag(msgs)
        print(result)

def test_gemini_checker() -> None:
    checker = GeminiChecker(api_key=GOOGLE_API_KEY)

    for msgs in test_sets:
        result = checker.check_rag(msgs)
        print(result)

def test_double_quote_parsing() -> None:
    data_str = """
{
  should_retrieve: false,
  query: ""
}
"""
    checker = OpenAIChecker(api_key=OPENAI_API_KEY) 
    result = checker.parse_response(data_str)
    print(result)
    


if __name__ == "__main__":
    # test_openai_checker()
    # test_gemini_checker()
    test_double_quote_parsing()