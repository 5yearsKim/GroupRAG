from gossipbao import GossipBao



async def test_respond():
    bao = GossipBao()

    messages = [
        {"role": "user", "content": "안녕"}
    ]

    rsp_stream = bao.respond(messages)

    async for rsp in rsp_stream:
        print(rsp)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_respond())