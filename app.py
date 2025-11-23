# app.py
import streamlit as st
from config.settings import *
from config.styles import apply_main_styles, apply_sidebar_styles
from utils.session import initialize_session_state
from auth.forms import login_form, signup_form
from components.sidebar import render_sidebar
from components.chat import render_main_chat
from components.map_sidebar import render_map_sidebar

# ========================
# KHỞI TẠO
# ========================
st.set_page_config(
    page_title="Food Chatbot",
    page_icon="🍽️",   # Biểu tượng đĩa thức ăn – chung chung, chuyên nghiệp
    layout="wide"
)
apply_main_styles()
initialize_session_state()

# ========================
# AUTHENTICATION
# ========================
auth, _ = get_firebase_clients()  # từ config/settings.py

if not st.session_state.logged_in:
    if st.session_state.get("show_signup", False):
        signup_form()
    else:
        login_form()
    st.stop()

apply_sidebar_styles()
# ========================
# GIAO DIỆN CHÍNH (SAU KHI LOGIN)
# ========================
# Layout
if st.session_state.show_map_sidebar:
    main_col, map_col = st.columns([2, 1])
else:
    main_col = st.container()
    map_col = None

# Sidebar + Menu
menu = render_sidebar()

# render map
render_map_sidebar(map_col)
