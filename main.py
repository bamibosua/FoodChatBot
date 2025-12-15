import streamlit as st
from UI.config.settings import *
from UI.config.styles import apply_main_styles, apply_sidebar_styles
from UI.utils.session import initialize_session_state
from UI.auth.forms import login_form, signup_form
from UI.components.sidebar import render_sidebar
from UI.components.render import render_main_chat, render_map_sidebar, init_food_state

st.set_page_config(
    page_title="Food Chatbot",
    layout="wide"
)
apply_main_styles()
initialize_session_state()

auth, _ = get_firebase_clients()

if not st.session_state.logged_in:
    if st.session_state.get("show_signup", False):
        signup_form()
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

restaurants = st.session_state.get("filtered_restaurants", {})

with map_col:
    render_map_sidebar(st.container(height=750), restaurant_places=restaurants)