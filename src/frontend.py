import streamlit as st
import httpx

API_URL = "http://127.0.0.1:8000/chat"


def init_session_states():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "message_history" not in st.session_state:
        st.session_state.message_history = []


def display_chat_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input():
    if prompt := st.chat_input("Talk to the JokeBot"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            api_response = httpx.post(
                API_URL,
                json={
                    "question": prompt,
                    "message_history": st.session_state.message_history,
                },
                timeout=30.0,
            )
            api_response.raise_for_status()
            api_data = api_response.json()

            st.session_state.message_history = api_data.get("message_history", [])
            bot_response = api_data.get("response", "Oops, I could not think of a joke.")

        except httpx.HTTPError as e:
            bot_response = f"Backend error: {e}"

        display_response = f"Ro Båt: {bot_response}"

        with st.chat_message("assistant"):
            st.markdown(display_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": display_response}
        )


def layout():
    st.markdown("# Chat with Ro Båt")
    st.write("RO BÅT is a funny robot that will answer with a programming joke.")

    display_chat_messages()
    handle_user_input()


if __name__ == "__main__":
    init_session_states()
    layout()