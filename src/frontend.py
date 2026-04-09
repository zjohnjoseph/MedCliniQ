import streamlit as st
import httpx
import streamlit.components.v1 as components
import html
import re

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

def remove_emojis(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    cleaned_text = emoji_pattern.sub("", text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    return cleaned_text            

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
            speak_text(bot_response)

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