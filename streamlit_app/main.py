import streamlit as st


st.title("Group RAG")

with st.sidebar:
    openai_api_key = st.text_input('OpenAI API Key', type='password')

def generate_response(input_text: str) -> None:
    out_text = 'this is a generated text'
    st.info(out_text)

with st.form('my_form'):
    text = st.text_area('Enter text:', 'What are the three key pieces of advice for learning how to code?')
    submitted = st.form_submit_button('Submit')
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    if submitted and openai_api_key.startswith('sk-'):
        generate_response(text)

