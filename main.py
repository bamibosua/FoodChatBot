import email
import streamlit as st
from UI.config.settings import *
from UI.config.styles import apply_main_styles, apply_sidebar_styles, get_signup_title_style, get_login_title_style, get_forgot_password_title_style, get_image_container_style
from UI.utils.session import initialize_session_state
from UI.auth.forms import login_form, signup_form, forgot_password_form
from UI.auth.logics import handle_signup, handle_login
from UI.components.sidebar import load_chat_history_from_file, render_sidebar, initialize_conversation
from UI.components.chat import render_main_chat
from UI.components.map_sidebar import render_map_sidebar

from UI.utils.helpers import  apply_header_sidebar_styles, get_chat_title
from UI.utils.helpers import save_chat_history_to_file, initialize_conversation, load_user_chats
from UI.utils.helpers import load_chat_history_from_file, save_current_chat, new_chat_id, get_chat_preview

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "show_forgot" not in st.session_state:
    st.session_state.show_forgot = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
st.set_page_config(
    page_title="Food Chatbot",
    layout="wide"
)

apply_main_styles()
initialize_session_state()

auth, _ = get_firebase_clients()

#=======Login/Signup/Forgot Password Section========#
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_form()
    elif st.session_state.show_forgot:        
        forgot_password_form()                
    else:
        login_form()
    st.stop()

# load chat when press f5 - ALWAYS reload from file
st.session_state.all_chats = load_user_chats(st.session_state.username)

# create new chat when logout or f5
if st.session_state.all_chats: # check if there is any chat history, if not move to "else"
    # Nếu chưa có current_chat_id, tao chat moi
    if not st.session_state.current_chat_id:
        if st.session_state.get('current_chat_id'):
            save_current_chat()
        cid = new_chat_id()  # tạo chat_id mới
        st.session_state.current_chat_id = cid  
    # Load history từ database cho current_chat_id
        if st.session_state.current_chat_id in st.session_state.all_chats: # check if current_chat_id exists in database
            st.session_state.history = cid.get("history", []).copy()
            st.session_state.conversation_history = initialize_conversation(
                st.session_state.current_chat_id,
                st.session_state.username
            )
            save_current_chat()
        else:
            # Nếu current_chat_id không tồn tại trong database, reset
            st.session_state.current_chat_id = None
            st.session_state.conversation_history = []
else:
    # Không có chats trong database
    st.session_state.conversation_history = []
#=======Main Application Section========#
apply_sidebar_styles()

if st.session_state.show_map_sidebar:
    main_col, map_col = st.columns([2, 1])
else:
    main_col = st.container()
    map_col = None

menu = render_sidebar()

with main_col:
    render_main_chat()

render_map_sidebar(map_col) 