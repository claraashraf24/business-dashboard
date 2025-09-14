import streamlit as st

# Simple hardcoded credentials (for demo / portfolio only)
CREDENTIALS = {
    "clara": "password123",  # username: password
    "demo": "demo123"
}

def login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None

    if not st.session_state.authenticated:
        st.title("🔒 Login Required")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login")

        if login_button:
            if username in CREDENTIALS and CREDENTIALS[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()  # 🔑 new method
            else:
                st.error("❌ Invalid username or password")

        return False
    else:
        st.sidebar.success(f"👋 Welcome, {st.session_state.username}")
        # Add a logout button
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
        return True
