import streamlit as st
import requests
import uuid
import os

# FastAPI endpoint - Use environment variable or default to localhost
API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
API_URL = f"{API_BASE_URL}/chat"
API_AUTH = (os.getenv("API_USERNAME", ""), os.getenv("API_PASSWORD", ""))

# Initialize session state for storing chat history and thread_id
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())  # Generate a unique thread_id per session

st.title("Inventix AI")

if st.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.thread_id = str(uuid.uuid4())  # Reset thread_id for new session

# st.chat_message renders markdown only, never raw HTML from the user or the bot
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

if user_input := st.chat_input("Type your message here:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)
    try:
        response = requests.post(
            API_URL,
            json={"messages": [user_input], "thread_id": st.session_state.thread_id},
            auth=API_AUTH,
            timeout=60,
        )
        if response.ok:
            bot_response = response.json() or "No response from bot"
        else:
            bot_response = f"Error: API returned status code {response.status_code}: {response.text}"
    except requests.RequestException as e:
        bot_response = f"Error connecting to API: {e}"
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    st.chat_message("assistant").markdown(bot_response)
