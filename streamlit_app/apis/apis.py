# import sys
# sys.path.append("./")
from typing import Any
from sseclient import SSEClient


import requests
from group_ragger.schema import Group, Message



HOST = "http://localhost:8010"
GROUP = Group(
    id=-1,
    name="streamlit",
)

def list_knowledge() -> tuple[list[dict], str|None]:
    rsp = requests.get(f"{HOST}/knowledge", params={"group_id": GROUP.id}, timeout=10)
    data = rsp.json()

    return data['points'], data['next_cursor']

def create_knowledge(content: str) -> Any:
    rsp = requests.post(f"{HOST}/knowledge", json={"content": content, "group_id": GROUP.id}, timeout=10)
    # check rsp status if it's 200
    if rsp.status_code != 200:
        raise ValueError(f"Failed to create knowledge: {rsp.text}")

    return rsp.json()

def bot_respond(messages: list[Message]) -> SSEClient:
    """Fetches streamed data from the API."""
    data = {"group": GROUP.dict(), "messages": [msg.to_dict() for msg in messages], "user_id": -1}
    response = requests.post(f'{HOST}/bot/respond', json=data, timeout=1000, stream=True, headers={'Accept': 'text/event-stream'})
    if response.status_code == 200:
        return SSEClient(response)
    else:
        raise ValueError(f"Failed to fetch bot response: {response.text}")



if __name__ == "__main__":

    print(list_knowledge())
