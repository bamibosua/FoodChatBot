import streamlit as st
from UI.config.settings import *
from UI.config.styles import apply_main_styles, apply_sidebar_styles, get_signup_title_style, get_login_title_style, get_forgot_password_title_style, get_image_container_style
from UI.utils.session import initialize_session_state
from UI.auth.forms import login_form, signup_form, forgot_password_form
from UI.auth.logics import handle_signup, handle_login
from UI.components.sidebar import render_sidebar
from UI.components.chat import render_main_chat
from UI.components.map_sidebar import render_map_sidebar

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "show_forgot" not in st.session_state:
    st.session_state.show_forgot = False

st.set_page_config(
    page_title="Food Chatbot",
    layout="wide"
)
apply_main_styles()
initialize_session_state()

auth, _ = get_firebase_clients()

if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_form()
    elif st.session_state.show_forgot:        
        forgot_password_form()                
    else:
        login_form()
    st.stop()

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