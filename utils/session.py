# utils/session.py
import streamlit as st    

def initialize_session_state():
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
        "show_forgot": False,
        "username": "",
        "show_map_sidebar": True,
        "route_start": "District 2, Ho Chi Minh city, Viet Nam",
        "route_end": "District 1, Ho Chi Minh city, Viet Nam",
        "saved_routes": [],
        "submit_route": False,
        "reload_trigger": False,
        "show_signup": False,
        "route_map": None,
        "route_info": ""
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value