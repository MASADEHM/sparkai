import streamlit as st
from datetime import datetime
import requests
import uuid
import json
import os

# Initialize session state for storing chat history and thread_id
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())  # Generate a unique thread_id per session

# FastAPI endpoint - Use environment variable or default to localhost
API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
API_URL = f"{API_BASE_URL}/chat"

# Streamlit app title
st.title("Inventix AI")

# Create a container for the chat history
chat_container = st.container()

# Input form for sending messages
with st.form(key='message_form', clear_on_submit=True):
    user_input = st.text_input("Type your message here:", key="user_input")
    submit_button = st.form_submit_button(label="Send")

# When the user submits a message
if submit_button and user_input:
    # Add user message to the chat history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    try:
        # Send message to FastAPI backend with correct payload
        payload = {
            "messages": [user_input],  # List of strings
            "thread_id": st.session_state.thread_id  # Session thread_id
        }
        response = requests.post(API_URL, json=payload, timeout=20)
        
        # Check if the request was successful
        if response.status_code == 200:
            try:
                # Try to parse JSON response
                json_response = response.json()
                # Check if it's a dictionary and has 'response' key
                if isinstance(json_response, dict):
                    bot_response = json_response.get("response", "No response from bot")
                else:
                    # Handle non-dict JSON (e.g., string, list)
                    bot_response = str(json_response) if json_response else "No response from bot"
            except json.JSONDecodeError:
                # Handle case where response is not valid JSON (e.g., plain string)
                bot_response = response.text or "No response from bot"
        else:
            # Capture and display API error details
            try:
                error_detail = response.json().get("detail", "No error details provided")
                bot_response = f"Error: API returned status code {response.status_code}: {error_detail}"
            except (ValueError, json.JSONDecodeError):
                bot_response = f"Error: API returned status code {response.status_code}: {response.text}"
            
    except requests.RequestException as e:
        bot_response = f"Error connecting to API: {str(e)}"
    
    # Add bot response to the chat history
    st.session_state.messages.append({
        "role": "bot",
        "content": bot_response,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

# Display chat history in the container
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div style='text-align: right; margin: 5px;'>
                    <span style='color: #000000; padding: 10px; border-radius: 10px; border-color: grey;'>
                        {msg['content']}
                    </span>
                    <div style='font-size: 0.8em; color: #A0A0A0;'>{msg['timestamp']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style='text-align: left; margin: 5px;'>
                    <span style=' color: #000000; padding: 10px; border-radius: 10px;border-color: red'>
                        {msg['content']}
                    </span>
                    <div style='font-size: 0.8em; color: #A0A0A0;'>{msg['timestamp']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

# Optional: Add a button to clear chat history
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.thread_id = str(uuid.uuid4())  # Reset thread_id for new session
    st.rerun()