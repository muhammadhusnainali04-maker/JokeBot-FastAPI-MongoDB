import streamlit as st
import requests
import os

st.set_page_config(page_title="Joke Bot AI", page_icon="🃏")

# --- CONFIGURATION ---
# Check if running on Render; if not, use localhost
if os.getenv("RENDER"):
    BASE_URL = "https://jokebot-fastapi-mongodb-2.onrender.com"
else:
    BASE_URL = "http://127.0.0.1:8000"

# --- 1. Login Logic ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = ""

with st.sidebar:
    st.title("User Login")
    if not st.session_state.logged_in:
        uid_input = st.text_input("Enter your User ID (e.g., user123)")
        if st.button("Login"):
            if uid_input:
                st.session_state.user_id = uid_input
                st.session_state.logged_in = True
                
                # Fetch history from the dynamic BASE_URL
                try:
                    hist_response = requests.get(f"{BASE_URL}/history/{uid_input}")
                    if hist_response.status_code == 200:
                        st.session_state.messages = hist_response.json().get("history", [])
                except Exception as e:
                    st.error(f"Could not load history: {e}")
                
                st.rerun()
            else:
                st.error("Please enter an ID")
    else:
        st.success(f"Logged in as: {st.session_state.user_id}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.messages = [] 
            st.rerun()

# --- 2. Chat Interface ---
st.title("🃏 The Joke Bot")

if st.session_state.logged_in:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input
    if prompt := st.chat_input("Ask for a joke..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Post to the dynamic BASE_URL
                response = requests.post(
                    f"{BASE_URL}/chat", 
                    json={"user_id": st.session_state.user_id, "question": prompt}
                )
                if response.status_code == 200:
                    answer = response.json().get("response")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Backend Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection Failed: {e}")
else:
    st.info("Please login from the sidebar to start chatting.")
