# import streamlit as st
# import httpx
# import streamlit.components.v1 as components
# import html
# import re
# from auth import app as auth_app
# API_URL = "http://127.0.0.1:8000/chat"


# def init_session_states():
#     if "messages" not in st.session_state:
#         st.session_state.messages = []

#     if "message_history" not in st.session_state:
#         st.session_state.message_history = []

#     if "authenticated" not in st.session_state:
#         st.session_state.authenticated = False


# def display_chat_messages():
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

# def remove_emojis(text: str) -> str:
#     # Remove all Emoji, Symbols, and Decorations in one line
#     emoji_pattern = re.compile(
#         r"[\U0001F000-\U0001FFFF\U00002700-\U000027FF\u2600-\u26FF\u2700-\u27BF]"
#     )
#     cleaned_text = emoji_pattern.sub("", text)
#     return re.sub(r"\s+", " ", cleaned_text).strip()       

# def speak_text(text: str):
#     cleaned_text = remove_emojis(text)
#     safe_text = html.escape(cleaned_text).replace("\n", " ")

#     components.html(
#         f"""
#         <div>
#             <button onclick="speakText()" style="
#                 background-color:#ff4b4b;
#                 color:white;
#                 border:none;
#                 padding:8px 14px;
#                 border-radius:8px;
#                 cursor:pointer;
#                 font-size:14px;
#             ">
#                 🔊 Speak response
#             </button>

#             <script>
#                 function speakText() {{
#                     const text = "{safe_text}";
#                     const utterance = new SpeechSynthesisUtterance(text);
#                     utterance.lang = "en-US";
#                     utterance.rate = 1;
#                     utterance.pitch = 1;
#                     window.speechSynthesis.cancel();
#                     window.speechSynthesis.speak(utterance);
#                 }}
#             </script>
#         </div>
#         """,
#         height=60,
#     )

# def handle_user_input():
#     if prompt := st.chat_input("Hi, how can I help you?"):
#         st.session_state.messages.append({"role": "user", "content": prompt})

#         with st.chat_message("user"):
#             st.markdown(prompt)

#         try:
#             api_response = httpx.post(
#                 API_URL,
#                 json={
#                     "question": prompt,
#                     "message_history": st.session_state.message_history,
#                 },
#                 timeout=30.0,
#             )
#             api_response.raise_for_status()
#             api_data = api_response.json()

#             st.session_state.message_history = api_data.get("message_history", [])
#             bot_response = api_data.get("response", "Sorry, I could not generate a response.")

#         except httpx.HTTPError as e:
#             bot_response = f"Backend error: {e}"

#         display_response = f"Chatbot: {bot_response}"

#         with st.chat_message("assistant"):
#             st.markdown(display_response)
#             speak_text(bot_response)

#         st.session_state.messages.append(
#             {"role": "assistant", "content": display_response}
#         )

# def clear_chat():
#     st.session_state.messages = []
#     st.session_state.message_history = []
#     st.rerun()


# def layout():
#     if not st.session_state.authenticated:
#         auth_app()
#         st.stop()

#     st.markdown("# Chat with :violet[Chatbot]")
#     st.write("Chatbot is a friendly chatbot that is here to assist you.")

#     col1, col2 = st.columns(2)

#     with col1:
#         if st.button("Clear Chat", icon=":material/delete_sweep:"):
#             clear_chat()

#     with col2:
#         if st.button("Logout", icon=":material/logout:"):
#             st.session_state.authenticated = False
#             st.session_state.signout = False
#             st.session_state.signedout = False
#             st.session_state.username = ""
#             st.session_state.useremail = ""
#             st.session_state.messages = []
#             st.session_state.message_history = []
#             st.rerun()

#     display_chat_messages()
#     handle_user_input()


# if __name__ == "__main__":
#     init_session_states()
#     layout()

import streamlit as st
import httpx
import streamlit.components.v1 as components
import html
import re
from auth import app as auth_app

API_URL = "http://127.0.0.1:8000/chat"


def init_session_states():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "message_history" not in st.session_state:
        st.session_state.message_history = []

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False


def display_chat_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def remove_emojis(text: str) -> str:
    emoji_pattern = re.compile(
        r"[\U0001F000-\U0001FFFF\U00002700-\U000027FF\u2600-\u26FF\u2700-\u27BF]"
    )
    cleaned_text = emoji_pattern.sub("", text)
    return re.sub(r"\s+", " ", cleaned_text).strip()


def speak_text(text: str):
    cleaned_text = remove_emojis(text)
    safe_text = html.escape(cleaned_text).replace("\n", " ")

    components.html(
        f"""
        <div>
            <button onclick="speakText()" style="
                background-color:#ff4b4b;
                color:white;
                border:none;
                padding:8px 14px;
                border-radius:8px;
                cursor:pointer;
                font-size:14px;
            ">
                🔊 Speak response
            </button>

            <script>
                function speakText() {{
                    const text = "{safe_text}";
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.lang = "en-US";
                    utterance.rate = 1;
                    utterance.pitch = 1;
                    window.speechSynthesis.cancel();
                    window.speechSynthesis.speak(utterance);
                }}
            </script>
        </div>
        """,
        height=60,
    )


def handle_user_input():
    if prompt := st.chat_input("Hi, how can I help you?"):
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
                timeout=300.0,
            )
            api_response.raise_for_status()
            api_data = api_response.json()

            st.session_state.message_history = api_data.get("message_history", [])
            bot_response = api_data.get(
                "response", "Sorry, I could not generate a response."
            )

        except httpx.HTTPError as e:
            bot_response = f"Backend error: {e}"

        with st.chat_message("assistant"):
            st.markdown(bot_response)
            speak_text(bot_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": bot_response}
        )


def clear_chat():
    st.session_state.messages = []
    st.session_state.message_history = []
    st.rerun()


def layout():
    if not st.session_state.authenticated:
        auth_app()
        st.stop()

    st.markdown("# Chat with :violet[Chatbot]")
    st.write("Chatbot is a friendly chatbot that is here to assist you.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Clear Chat", icon=":material/delete_sweep:"):
            clear_chat()

    with col2:
        if st.button("Logout", icon=":material/logout:"):
            st.session_state.authenticated = False
            st.session_state.signout = False
            st.session_state.signedout = False
            st.session_state.username = ""
            st.session_state.useremail = ""
            st.session_state.messages = []
            st.session_state.message_history = []
            st.rerun()

    display_chat_messages()
    handle_user_input()


if __name__ == "__main__":
    init_session_states()
    layout()