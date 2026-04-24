import streamlit as st
import httpx
import streamlit.components.v1 as components
import html
import re
from auth import app as auth_app
from db import create_conversation, get_conversations, get_messages, delete_conversation

API_URL = "http://127.0.0.1:8000/chat"


def init_session_states():
    defaults = {
        "messages": [],
        "message_history": [],
        "authenticated": False,
        "active_conversation_id": None,
        "conversations": [],
        "user_id": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def remove_emojis(text: str) -> str:
    emoji_pattern = re.compile(
        r"[\U0001F000-\U0001FFFF\U00002700-\U000027FF☀-⛿✀-➿]"
    )
    return re.sub(r"\s+", " ", emoji_pattern.sub("", text)).strip()


def speak_text(text: str):
    cleaned_text = remove_emojis(text)
    safe_text = html.escape(cleaned_text).replace("\n", " ")
    components.html(
        f"""
        <div>
            <button onclick="speakText()" style="
                background-color:#ff4b4b;color:white;border:none;
                padding:8px 14px;border-radius:8px;cursor:pointer;font-size:14px;">
                🔊 Speak response
            </button>
            <script>
                function speakText() {{
                    const utterance = new SpeechSynthesisUtterance("{safe_text}");
                    utterance.lang = "en-US"; utterance.rate = 1; utterance.pitch = 1;
                    window.speechSynthesis.cancel();
                    window.speechSynthesis.speak(utterance);
                }}
            </script>
        </div>
        """,
        height=60,
    )


def refresh_conversations(user_id: str):
    st.session_state.conversations = get_conversations(user_id)


def load_conversation(user_id: str, conversation_id: str):
    messages = get_messages(user_id, conversation_id)
    st.session_state.messages = messages
    st.session_state.message_history = [
        {"role": m["role"], "content": m["content"]} for m in messages
    ]
    st.session_state.active_conversation_id = conversation_id


def start_new_chat(user_id: str):
    conv_id = create_conversation(user_id)
    st.session_state.active_conversation_id = conv_id
    st.session_state.messages = []
    st.session_state.message_history = []
    refresh_conversations(user_id)


def render_sidebar(user_id: str):
    with st.sidebar:
        st.markdown("## :violet[MedCliniQ]")

        if st.button("+ New Chat", use_container_width=True, type="primary"):
            start_new_chat(user_id)
            st.rerun()

        st.divider()

        convs = st.session_state.conversations
        if not convs:
            st.caption("No conversations yet.")
        else:
            for conv in convs:
                is_active = conv["id"] == st.session_state.active_conversation_id
                col1, col2 = st.columns([5, 1])
                with col1:
                    if st.button(
                        conv.get("title", "New Chat"),
                        key=f"conv_{conv['id']}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary",
                    ):
                        load_conversation(user_id, conv["id"])
                        st.rerun()
                with col2:
                    if st.button("🗑", key=f"del_{conv['id']}"):
                        delete_conversation(user_id, conv["id"])
                        if is_active:
                            st.session_state.active_conversation_id = None
                            st.session_state.messages = []
                            st.session_state.message_history = []
                        refresh_conversations(user_id)
                        st.rerun()

        st.divider()
        username = st.session_state.get("username") or st.session_state.get("useremail", "")
        st.caption(f"Logged in as **{username}**")

        if st.button("Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def display_chat_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(user_id: str):
    if prompt := st.chat_input("Ask MedCliniQ a health question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            api_response = httpx.post(
                API_URL,
                json={
                    "question": prompt,
                    "message_history": st.session_state.message_history,
                    "conversation_id": st.session_state.active_conversation_id,
                    "user_id": user_id,
                },
                timeout=120.0,
            )
            api_response.raise_for_status()
            api_data = api_response.json()
            st.session_state.message_history = api_data.get("message_history", [])
            bot_response = api_data.get("response", "Sorry, I could not generate a response.")
        except httpx.ConnectError:
            bot_response = "I'm currently unavailable. Please try again in a moment."
        except httpx.TimeoutException:
            bot_response = "The request timed out. Please try again."
        except httpx.HTTPError:
            bot_response = "Something went wrong. Please try again shortly."

        with st.chat_message("assistant"):
            st.markdown(bot_response)
            speak_text(bot_response)

        st.session_state.messages.append({"role": "assistant", "content": bot_response})

        # Refresh sidebar after first message so auto-generated title appears
        if len(st.session_state.messages) == 2:
            refresh_conversations(user_id)
            if st.session_state.conversations:
                st.rerun()


def layout():
    if not st.session_state.authenticated:
        auth_app()
        st.stop()

    user_id = st.session_state.get("user_id") or st.session_state.get("useremail", "")

    # On first load after login, populate conversations
    if not st.session_state.conversations:
        refresh_conversations(user_id)
        if st.session_state.conversations:
            load_conversation(user_id, st.session_state.conversations[0]["id"])
        elif not st.session_state.messages:
            start_new_chat(user_id)

    render_sidebar(user_id)

    st.markdown("# Chat with :violet[MedCliniQ]")
    st.caption("Your AI medical assistant. Always consult a healthcare professional for personal medical decisions.")

    display_chat_messages()
    handle_user_input(user_id)


if __name__ == "__main__":
    init_session_states()
    layout()
