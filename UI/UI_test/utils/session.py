# utils/session.py
import streamlit as st

def initialize_session_state():
    """
    Khởi tạo tất cả các key cần thiết trong st.session_state
    Chỉ chạy 1 lần khi app khởi động
    """
    defaults = {
        "all_chats": {},
        "current_chat_id": None,
        "history": [],
        "conversation_history": [],
        "favorites": [],
        "last_assistant_id": None,
        "chat_titles": {},
        "show_settings": False,
        "logged_in": False,
        "username": "",
        "show_map_sidebar": True,
        "route_start": "Quận 2, Thành phố Hồ Chí Minh, Việt Nam",
        "route_end": "Quận 1, Thành phố Hồ Chí Minh, Việt Nam",
        "saved_routes": [],
        "submit_route": False,
        "reload_trigger": False,
        "show_signup": False,        # QUAN TRỌNG: cho login/signup
        "route_map": None,
        "route_info": ""
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value