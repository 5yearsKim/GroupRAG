from group_ragger import GroupRagger
from group_ragger.schema import Message, MessageRole, Group



async def test_respond() -> None:
    ragger = GroupRagger( generator_type='claude')

    messages= [
        Message(role=MessageRole.USER, content="안녕")
    ]

    group = Group(id=1, name="test")

    rsp_stream = ragger.respond(messages, group)

    async for rsp in rsp_stream:
        print(rsp)



def test_gemini() -> None:
    import google.generativeai as genai
    from gossipbao.config import GOOGLE_API_KEY

    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel('gemini-pro')

    response = model.generate_content("안녕 길게 대답해줘!", stream=True)

    print(response)

    for chunk in response:
        print(chunk)



if __name__ == "__main__":
    import asyncio
    asyncio.run(test_respond())

    # test_gemini()

