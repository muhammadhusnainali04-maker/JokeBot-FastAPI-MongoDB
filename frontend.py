import streamlit as st
import requests

st.set_page_config(page_title="Joke Bot AI", page_icon="🃏")

# --- 1. Login Logic ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = ""

with st.sidebar:
    st.title("User Login")
    if not st.session_state.logged_in:
        uid_input = st.text_input("Enter your User ID (e.g., user123)")
        if st.button("Login"):
                    # Inside the "if st.button('Login'):" block in frontend.py

            if uid_input:
                st.session_state.user_id = uid_input
                st.session_state.logged_in = True
                
                # --- NEW: Fetch history from backend ---
                try:
                    hist_response = requests.get(f"http://127.0.0.1:8000/history/{uid_input}")
                    if hist_response.status_code == 200:
                        # Sync the database history with the Streamlit session
                        st.session_state.messages = hist_response.json().get("history", [])
                except Exception as e:
                    st.error(f"Could not load history: {e}")
                
                st.rerun()
            if uid_input:
                st.session_state.user_id = uid_input
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Please enter an ID")
    else:
        st.success(f"Logged in as: {st.session_state.user_id}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.messages = [] # Clear UI history on logout
            st.rerun()

# --- 2. Chat Interface ---
st.title("🃏 The Joke Bot")

if st.session_state.logged_in:
    # Initialize session state for UI messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
        # Optional: Fetch existing history from MongoDB on first login
        # This keeps the UI synced with your database
        try:
            # You can add a GET endpoint to your FastAPI to fetch history if you want it to persist across refreshes
            pass 
        except:
            pass

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
                response = requests.post(
                    "http://127.0.0.1:8000/chat", 
                    json={"user_id": st.session_state.user_id, "question": prompt}
                )
                if response.status_code == 200:
                    answer = response.json().get("response")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error("Backend Error")
            except Exception as e:
                st.error(f"Connection Failed: {e}")
else:
    st.info("Please login from the sidebar to start chatting.")