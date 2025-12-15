import streamlit as st
from UI.config.settings import auth
from UI.utils.helpers import load_user_chats

#========================================SIGN UP & LOGIN HANDLERS ========================
def handle_signup(email: str, password: str) -> bool:
    if not email or not password:
        st.error("Please enter both email and password.")
        return False
    try:
        user = auth.create_user_with_email_and_password(email, password)
        st.success("Sign up successful! Please log in.")
        st.session_state.show_signup = False
        st.rerun()
        return True
    except Exception as e:
        error_message = str(e)
        if "WEAK_PASSWORD" in error_message:
            st.error("Weak password. Please use at least 6 characters.")
        elif "EMAIL_EXISTS" in error_message:
            st.error("Email already exists. Please use a different email.")
        elif "INVALID_EMAIL" in error_message:
            st.error("Invalid email format")
        else:
            st.error(f"Sign up error: {error_message}")
        return False

def handle_login(email: str, password: str) -> bool:
    if not email or not password:
        st.error("Please enter both email and password.")
        return False
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state.logged_in = True
        st.session_state.username = email.split('@')[0]
        
        # LOAD LỊCH SỬ CHAT KHI ĐĂNG NHẬP
        st.session_state.all_chats = load_user_chats(st.session_state.username)
        
        st.success("Login successful!")
        st.rerun()
        return True
    except Exception as e:
        error_message = str(e)
        if "INVALID_PASSWORD" in error_message or "INVALID_LOGIN_CREDENTIALS" in error_message:
            st.error("Invalid email or password")
        elif "INVALID_EMAIL" in error_message:
            st.error("Invalid email format")
        elif "EMAIL_NOT_FOUND" in error_message:
            st.error("Email not found. Please sign up first.")
        elif "TOO_MANY_ATTEMPTS" in error_message:
            st.error("Too many failed attempts. Please try again later.")
        else:
            st.error("Invalid email or password")
        return False
