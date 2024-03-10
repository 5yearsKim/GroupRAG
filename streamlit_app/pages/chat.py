import json

import streamlit as st
from group_ragger.schema import Message, MessageRole

from streamlit_app.apis import bot_respond



MESSAGES = 'messages'

def handle_respond() -> None:
    messages = st.session_state[MESSAGES]

    if messages:
        with st.spinner('AI is thinking...'):
            sse_client = bot_respond(messages)
            ans = Message(role=MessageRole.BOT, content='')

            st.session_state[MESSAGES].append(ans)
            for event in sse_client.events():
                data = event.data
                if data.startswith('data: '):
                    data = data[6:]
                parsed = json.loads(data)
                ans.content = parsed['text']



def main() -> None:
    st.markdown("# Chat 💬")
    st.sidebar.markdown("# Chat 💬️")

    if MESSAGES not in st.session_state:
        st.session_state[MESSAGES] = []

    for msg in st.session_state[MESSAGES]:
        role = 'user' if msg.role == MessageRole.USER else 'ai'
        st.chat_message(role).write(msg.content)


    prompt = st.chat_input("Enter your message")

    if prompt:
        st.session_state[MESSAGES].append(Message(role=MessageRole.USER, content=prompt))
        handle_respond()
        st.rerun()






main()
