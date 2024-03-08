from test_utils import set_python_path
set_python_path()

from group_ragger import GroupRagger
from group_ragger.schema import Message, MessageRole, Group
import google.generativeai as genai
from group_ragger.config import GOOGLE_API_KEY



def test_gemini() -> None:

    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel('gemini-pro')

    response = model.generate_content("안녕 길게 대답해줘!", stream=True)

    print(response)

    for chunk in response:
        print(chunk)



if __name__ == "__main__":
    test_gemini()
