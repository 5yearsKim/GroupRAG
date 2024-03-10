import streamlit as st

from streamlit_app.apis import list_knowledge, create_knowledge



def main() -> None:
    st.markdown("# Knowledge ❄️")
    st.sidebar.markdown("# Knowledge ❄️")

    data, _ = list_knowledge()

    with st.form("my_form"):
        st.write("Add knowledge to the group.")

        content = st.text_area('Content',
            placeholder='ex) ㅁㅁㅁ는 ㅇㅇㅇ를 좋아한다.',
        )
        submit_button = st.form_submit_button("Submit")
        if submit_button:
            rsp = create_knowledge(content)

            st.success('knowledge added successfully!')

            # Re-fetch data after submission
            data, _ = list_knowledge()


    if data:
        # Option 1: Display data as a table
        st.subheader("Knowledge Points")
        st.dataframe(data)

        # # Option 2: Create a chart (example: bar chart using content length)
        # print(data)
        # content_lengths = [len(point['content']) for point in data]
        # st.subheader("Content Length Distribution")
        # st.bar_chart(content_lengths)
    else:
        st.info("No data available to visualize.")

main()
