# tourism_chatbot_app.py
import logging
import json
import base64
import datetime
import time
from datetime import datetime
from typing import List, Dict
from streamlit_folium import st_folium
from PIL import Image, ImageEnhance
from openai import OpenAI, OpenAIError
import streamlit as st
import pyrebase
import firebase_admin
import requests
from datetime import datetime, timezone
from firebase_admin import credentials, firestore
from ollama import Client
from streamlit_extras.stylable_container import stylable_container
#add them thu vien
import numpy as np
import pandas as pd
from firebase_admin import auth

# ───────────────────────────────────────────────
# FIREBASE SETUP — giữ nguyên logic ban đầu
# ───────────────────────────────────────────────
@st.cache_resource
def get_firebase_clients():
    firebase_cfg = st.secrets["firebase_client"]
    firebase_app = pyrebase.initialize_app(firebase_cfg)
    auth = firebase_app.auth()

    if not firebase_admin._apps:
        cred = credentials.Certificate(dict(st.secrets["firebase_admin"]))
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    return auth, db

auth, db = get_firebase_clients()

# Thêm vào đầu file, sau phần import
# Khởi tạo session state
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False


# Import OSM routing module
try:
    from map import create_route_map
    OSM_AVAILABLE = True
except ImportError:
    logging.warning("osm_routing module not found. Map features will be limited.")
    OSM_AVAILABLE = False

if "reload_trigger" not in st.session_state:
    st.session_state.reload_trigger = False

# -----------------------
# CONFIG + LOGGING
# -----------------------
logging.basicConfig(level=logging.INFO)

# Replace with your retrieval of the OpenAI API key (secrets.toml or env)
OPENAI_API_KEY = "your-openai-api-key"
if not OPENAI_API_KEY:
    st.error("Please add your OpenAI API key to the Streamlit secrets.toml file.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# App constants
NUMBER_OF_MESSAGES_TO_DISPLAY = 50
DEFAULT_MODEL = "gpt-4o-mini"

# -----------------------
# UTILS
# -----------------------
def img_to_base64(image_path: str):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        logging.debug(f"Could not load image {image_path}: {e}")
        return None

def new_chat_id() -> str:
    """Generate a new chat id using timestamp for uniqueness."""
    return datetime.now().strftime("chat_%Y%m%d%H%M%S%f")

def save_current_chat():
    """Save the current open chat history into all_chats."""
    cid = st.session_state.current_chat_id
    if cid and st.session_state.get('logged_in', False):
        st.session_state.all_chats[cid] = {
            "history": st.session_state.history.copy(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": st.session_state.chat_titles.get(cid, cid)
        }
        logging.info(f"Saved chat {cid} with {len(st.session_state.history)} messages.")

def initialize_conversation() -> List[Dict]: 
    # Khởi tạo cuộc trò chuyện với tin nhắn ban đầu
    assistant_message = "Xin chào! Tôi là dân sì gòn gốc, bạn muốn ăn gì? Tôi dẫn bạn dạt khắp sì gòn."
    return [
        # Thiết lập vai trò hệ thống cho trợ lý du lịch: "You ... restaurants" là định hướng chung cho trợ lý.
        {"role": "system", "content": "You are a helpful tourism assistant. Provide recommendations for restaurants"},
        {"role": "assistant", "content": assistant_message} # Khởi tạo tin nhắn ban đầu từ trợ lý
    ]

def get_chat_preview(history):
    # Lấy đoạn xem trước của cuộc trò chuyện
    if not history:
        return "Empty chat"
    for msg in history: # msg là dict với keys: role, content
        if msg.get("role") == "user":
            preview = msg.get("content", "")[:50]
            return preview + "..." if len(msg.get("content", "")) > 50 else preview # Lấy tối đa 50 ký tự làm đoạn xem trước
    return "New conversation"

# -----------------------
# SESSION STATE INIT
# -----------------------
def initialize_session_state():
    if "all_chats" not in st.session_state:
        st.session_state.all_chats = {}
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "favorites" not in st.session_state:
        st.session_state.favorites = []
    if "last_assistant_id" not in st.session_state:
        st.session_state.last_assistant_id = None
    if "chat_titles" not in st.session_state:
        st.session_state.chat_titles = {}
    if "show_settings" not in st.session_state:
        st.session_state.show_settings = False
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "show_map_sidebar" not in st.session_state:
        st.session_state.show_map_sidebar = True
    if "route_start" not in st.session_state:
        st.session_state.route_start = "Quận 2, Thành phố Hồ Chí Minh, Việt Nam"
    if "route_end" not in st.session_state:
        st.session_state.route_end = "Quận 1, Thành phố Hồ Chí Minh, Việt Nam"
    if "saved_routes" not in st.session_state:
        st.session_state.saved_routes = []

initialize_session_state()

# -----------------------
# PAGE CONFIG + THEME
# -----------------------

st.set_page_config(
    page_title="Food Chatbot",
    page_icon="🍽️",   # Biểu tượng đĩa thức ăn – chung chung, chuyên nghiệp
    layout="wide"
)

st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
""", unsafe_allow_html=True)

# Modern CSS styling
st.markdown("""
<style>
    /* Main background */
    [data-testid="stAppViewContainer"] {
        #background-color: #fff9c4; /* Màu vàng nhạt */
        background: linear-gradient(135deg, #fff176 0%, #6a1b9a 100%);
        height: 100vh;  /* Đảm bảo gradient hiển thị đầy đủ */

            
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        #background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%); /* Tối gradient */
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%); /* Xanh dương gradient */
            
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #ecf0f1; /* Màu chữ sáng trên sidebar tối */
    }
    
    /* Chat message styling */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: purple;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Input styling */
    [data-testid="stChatInput"] {
        border-radius: 25px;
        border: 2px solid #667eea;
    }
    
    /* Custom headers */
    .custom-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Login card */
    .login-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        max-width: 400px;
        margin: 50px auto;
    }
    
    /* User profile badge */
    .user-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 10px 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 10px 0;
        font-weight: bold;
    }
    
    /* Route info card */
    .route-info {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 15px;
        border-radius: 10px;
        color: purple;
        text-align: center;
        margin: 10px 0;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

import streamlit as st

st.markdown("""
<style>
/* Sidebar chính */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%) !important; /* Gradient xanh dương */
    color: #ecf0f1; /* Màu chữ sáng */
    padding: 20px; /* Padding trong sidebar */
    border-top-right-radius: 20px; /* Bo góc trên phải */
    border-bottom-right-radius: 20px; /* Bo góc dưới phải */
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.2); /* Bóng bên cạnh */
}

/* Chữ trong markdown của sidebar */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #ecf0f1 !important;
}

/* Các nút trong sidebar */
[data-testid="stSidebar"] button {
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: purple !important;
    border-radius: 10px !important;
    margin: 5px 0;
    padding: 8px 12px;
    border: none !important;
    font-weight: 600;
    transition: all 0.3s ease;
}

/* Hover nút sidebar */
[data-testid="stSidebar"] button:hover {
    background-color: rgba(255, 255, 255, 0.2) !important;
    transform: translateX(2px);
}
</style>
""", unsafe_allow_html=True)


def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def login_form(guest_mode=False):
    st.markdown(
    """
    <h1 style='color: black; font-family: Times New Roman; font-weight: 700; '>Food Chatbot</h1>
    <p style='font-size: 20px;'>
        <span style='color: black;font-family: Times New Roman;'>
            <i>You would like to eat. Log in to chat with us 👇<i>
        </span>
    <!-- Divider -->
    <div style='text-align: center; margin: 20px 0;'>
        <hr style='border: 1px solid #7e3412; width: 100%; margin: 0 auto;'>
    </div>
        
    </p>
    """,
    unsafe_allow_html=True
)
    with st.empty().container(border=False):
        col1, _, col2 = st.columns([1,0.05,1])
        
        with col1:
            # Sử dụng ảnh local từ thư mục data
            image_path = "imgs/background.png"
            image_base64 = get_base64_image(image_path)

            css = f'''
            <style>
                .stApp {{
                    background-image: url(data:image/jpeg;base64,{image_base64});
                    background-size: cover;
                    background-position: center;
                    background-attachment: fixed;
                }}
                .stApp > header {{
                    background-color: transparent;
                }}
                /* Đổi màu chữ input thành đen */
                .stTextInput label {{
                    color: black !important;
                    font-weight: bold;
                }}
                .stTextInput input {{
                    color: black !important;
                }}
            </style>
            '''

            st.markdown(css, unsafe_allow_html=True)
            st.write("")
            st.write("")
            st.markdown("<br>", unsafe_allow_html=True)
            # Hiển thị ảnh với căn chỉnh
            img_base64 = get_base64_image("imgs/demo1.jpg")
            st.markdown(
                f'''
                <div style="text-align: center;">
                    <img src="data:image/jpeg;base64,{img_base64}" 
                         style="width: 500px; height: 300px; object-fit: cover; border-radius: 20px;">
                         <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
                            <img style="width: 100%; height: auto; max-height: 400px; ...">
                         </div>
                </div>
                ''',
            unsafe_allow_html=True)
            #st.image("data/demo1.jpg", use_container_width=True)
        
        with col2:
            st.markdown(
                """
                <h2 style= 
                    'text-align : center; 
                    color: black;
                    font-family: Times New Roman; 
                    margin: 0px'>Login</h2>
                """,
                unsafe_allow_html = True
            )
            
            # Thêm CSS cho text input
            st.markdown(
                """
                <style>
                    div[data-testid="stTextInput"] label {
                        color: black !important;
                        font-weight: 600;
                    }
                    div[data-testid="stTextInput"] input {
                        color: black !important;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            email = st.text_input("E-mail")
            password = st.text_input("Password", type="password")

            # Tạo 3 cột để căn giữa buttons
            col_login, col_signup = st.columns([1, 1])

            with col_login:
                if st.button("Login", use_container_width=True):
                    try:
                         user = auth.sign_in_with_email_and_password(email, password)
                         st.session_state.logged_in = True
                         st.session_state.username = email.split('@')[0]
                         st.success("Login successful!")
                         st.rerun()
                    except Exception as e:
                            error_message = str(e)
                            if "INVALID_PASSWORD" in error_message or "INVALID_LOGIN_CREDENTIALS" in error_message:
                                st.error("Invalid email or password")
            with col_signup:
                if st.button("Sign Up", use_container_width=True):
                    st.session_state.show_signup = True
                    st.rerun()

def signup_form():
     st.markdown(
    """
    <h1 style='color: black; font-family: Times New Roman; font-weight: 700; '>Food Chatbot</h1>
    <p style='font-size: 20px;'>
        <span style='color: black;font-family: Times New Roman;'>
            <i>You would like to eat. Log in to chat with us 👇<i>
        </span>
    <!-- Divider -->
    <div style='text-align: center; margin: 20px 0;'>
        <hr style='border: 1px solid #7e3412; width: 100%; margin: 0 auto;'>
    </div>
        
    </p>
    """,
    unsafe_allow_html=True)
    
     with st.empty().container(border=False):
        col1, _, col2 = st.columns([10,1,10])
        
        with col1:
            # Sử dụng ảnh local từ thư mục data
            image_path = "imgs/background.png"
            image_base64 = get_base64_image(image_path)

            css = f'''
            <style>
                .stApp {{
                    background-image: url(data:image/jpeg;base64,{image_base64});
                    background-size: cover;
                    background-position: center;
                    background-attachment: fixed;
                }}
                .stApp > header {{
                    background-color: transparent;
                }}
                /* Đổi màu chữ input thành đen */
                .stTextInput label {{
                    color: black !important;
                    font-weight: bold;
                }}
                .stTextInput input {{
                    color: black !important;
                }}
            </style>
            '''

            st.markdown(css, unsafe_allow_html=True)
            st.write("")
            st.write("")
            st.markdown("<br>", unsafe_allow_html=True)
            # Hiển thị ảnh với căn chỉnh
            img_base64 = get_base64_image("imgs/demo1.jpg")
            st.markdown(
                f'''
                <div style="text-align: center;">
                    <img src="data:image/jpeg;base64,{img_base64}" 
                         style="width: 500px; height: 300px; object-fit: cover; border-radius: 10px;">
                </div>
                ''',
            unsafe_allow_html=True)
        st.markdown(css, unsafe_allow_html=True)
        with col2:
            st.markdown(
                """
                <h2 style= 
                    'text-align : center; 
                    color: black;
                    font-family: Times New Roman; 
                    margin: 0px'>Sign up</h2>
                """,
                unsafe_allow_html = True
            )
            
            # Thêm CSS cho text input
            st.markdown(
                """
                <style>
                    div[data-testid="stTextInput"] label {
                        color: black !important;
                        font-weight: 600;
                    }
                    div[data-testid="stTextInput"] input {
                        color: black !important;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
            email = st.text_input("Email")
            password = st.text_input("Password (≥6 characters)", type="password")
            col_create, col_back = st.columns(2)
            
            if st.button("Create Account", type="primary", use_container_width=True):
                    try:
                        user = auth.create_user_with_email_and_password(email, password)
                        st.success("Sign up successfully. Please login now!")
                         # Cho người dùng thấy thông báo thành công
                        st.session_state.show_signup = False
                        st.rerun()
                    except Exception as e:
                        error_message = str(e)
                        if "INVALID_PASSWORD" in error_message or "INVALID_LOGIN_CREDENTIALS" in error_message:
                                st.error("Invalid email or password")
                        elif "EMAIL_NOT_FOUND" in error_message:
                                st.error("Email not found. Please sign up first.")
                        elif "TOO_MANY_ATTEMPTS" in error_message:
                                st.error("Too many failed attempts. Please try again later.")
                        elif "WEAK_PASSWORD" in error_message:
                                st.error("Weak password. Please use at least 6 characters.")    
                        elif "EMAIL_EXISTS" in error_message:
                                st.error("Email already exists. Please use a different email.")
                        else:
                                st.error(f"Login error: {error_message}")
            
            with col_back:
                if st.button("Back", type="secondary", use_container_width=True):
                    st.session_state.show_signup = False
                    st.rerun()


# ========================
# CHECK LOGIN - ĐẶT Ở CUỐI FILE
# ========================
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_form()
    else:
        login_form()
    st.stop()


import base64

def load_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = load_image_base64("imgs/logo.png")  # đổi tên file theo đúng đường dẫn


st.markdown(f"""
<div class="custom-header">
    <h1>
        <img src="data:image/png;base64,{img_base64}" width="100" style="vertical-align: middle; margin-right: 5px;">
        Tourism Chatbot
    </h1>
    <p>Your intelligent travel companion with route planning</p>
</div>
""", unsafe_allow_html=True)


# -----------------------
# LAYOUT: Main + Right Sidebar
# -----------------------
if st.session_state.show_map_sidebar:
    main_col, map_col = st.columns([2, 1])
else:
    main_col = st.container()
    map_col = None

# -----------------------
# LEFT SIDEBAR
# -----------------------
with st.sidebar:
    # User profile section12
    st.markdown(f"""
    <div class="user-badge">
        <i class="fa-solid fa-user-astronaut"></i> {st.session_state.username}
    </div>
    """, unsafe_allow_html=True)

    if st.button("Log out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
    
    st.markdown("---")
    
    # Toggle map sidebar
    if st.checkbox("🗺 Show Map", value=st.session_state.show_map_sidebar):
        st.session_state.show_map_sidebar = True
    else:
        st.session_state.show_map_sidebar = False
    
    # Menu with icons
    menu = st.radio(
        "Select Function:",
        ["New Chat!", "History", "Favorites", "Settings"],
        index=0
    )
             
    # Quick stats
    st.markdown('<i class="fa-solid fa-chart-column"></i> Statistics', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Chats", len(st.session_state.all_chats))
    with col2:
        st.metric("Favorites", len(st.session_state.favorites))
    
    st.markdown("---")   

# -----------------------
# MENU: NEW CHAT
# -----------------------
if menu == "New Chat!":
    with st.sidebar:
        st.markdown('<i class="fa-regular fa-comment-dots"></i> Start New Chat!', unsafe_allow_html=True)
        
        if st.button("Create New Chat!", use_container_width=True):
            if st.session_state.current_chat_id:
                save_current_chat()
            
            cid = new_chat_id()
            st.session_state.current_chat_id = cid
            st.session_state.history = [{"role": "assistant", "content": "Hello! "}]
            st.session_state.conversation_history = initialize_conversation()
            st.rerun()
        st.markdown("---")
        st.markdown(
    '<div style="background-color:#d1ecf1; color:#0c5460; padding:10px; border-radius:5px;">'
    '<i class="fa-regular fa-lightbulb"></i> Trick: Press ❤ to save favorites!'
    '</div>',
    unsafe_allow_html=True
    )   

# -----------------------
# MENU: CONVERSATION HISTORY
# -----------------------
elif menu == "History":
    with st.sidebar:
        st.markdown('<i class="fa-regular fa-comment"></i> Conversation History', unsafe_allow_html=True)
        
        if st.session_state.all_chats:
            search_term = st.text_input('<i class="fa-regular fa-comment"></i> Search Conversations', "")
            
            ordered = sorted(st.session_state.all_chats.items(), key=lambda kv: kv[1].get("timestamp", ""), reverse=True)
            
            for chat_id, chat_data in ordered:
                history = chat_data.get("history", [])
                timestamp = chat_data.get("timestamp", "")
                title = chat_data.get("title", chat_id)
                preview = get_chat_preview(history)
                
                if search_term and search_term.lower() not in preview.lower() and search_term.lower() not in title.lower():
                    continue
                
                with st.expander(f'<i class="fa-regular fa-newspaper"></i> {title[:30]}...', expanded=False):
                    st.markdown(f'<i class="fa-regular fa-clock"></i> {timestamp}', unsafe_allow_html=True)
                    st.markdown(f'<i class="fa-regular fa-comment-dots"></i> {preview}', unsafe_allow_html=True)
                                
                    col1, col2 = st.columns(2)
                    if col1.button("", key=f"load_{chat_id}"):
                        if st.session_state.current_chat_id:
                            save_current_chat()
                        st.session_state.current_chat_id = chat_id
                        st.session_state.history = history.copy()
                        st.session_state.conversation_history = initialize_conversation()
                        st.rerun()
                    
                    if col2.button("Remove", key=f"del_{chat_id}"):
                        st.session_state.all_chats.pop(chat_id, None)
                        st.session_state.chat_titles.pop(chat_id, None)
                        if st.session_state.current_chat_id == chat_id:
                            st.session_state.current_chat_id = None
                            st.session_state.history = []
                            st.session_state.conversation_history = []
                        st.rerun()
        else:
            st.markdown(
            '<div style="background-color:#d1ecf1; color:#0c5460; padding:10px; border-radius:5px;">'
            '<i class="fa-regular fa-paper-plane"></i> There are no saved conversations yet.'
            '</div>',
            unsafe_allow_html=True)

# -----------------------
# MENU: FAVORITES
# -----------------------
elif menu == "Favorites":
    with st.sidebar:
        st.markdown('<i class="fa-regular fa-heart"></i> Favorites', unsafe_allow_html=True)
        
        if st.session_state.favorites:
            fav_search = st.text_input("Favorites Search", "")
            
            for i, fav in enumerate(st.session_state.favorites, start=1):
                if fav_search and fav_search.lower() not in fav.lower():
                    continue
                
                with st.expander(f" Item {i}"):
                    st.write(fav[:100] + "..." if len(fav) > 100 else fav)
                    if st.button("Remove", key=f"remove_fav_{i}"):
                        st.session_state.favorites.remove(fav)
                        st.rerun()
            
            st.markdown("---")
            if st.button("Remove All Favorites", use_container_width=True):
                st.session_state.favorites = []
                st.rerun()
        else:
            st.markdown(
    '<div style="background-color:#f8d7da; color:#721c24; padding:10px; border-radius:5px;">'
    '<i class="fa-solid fa-heart-crack"></i> There are no favorites yet.'
    '</div>',
    unsafe_allow_html=True
)
            
# -----------------------
# MENU: SETTINGS
# -----------------------
elif menu == "Settings":
    with st.sidebar:
        st.markdown('<i class="fa-solid fa-gear"></i> Settings', unsafe_allow_html=True)
        
        theme = st.selectbox(
            "Color Theme:",
            ["Light Yellow (default)", "Blue", "Green", "Orange", "Pink", "Purple"],
            index=0
        )
        
        msg_count = st.slider("Number of messages to display:", 10, 100, NUMBER_OF_MESSAGES_TO_DISPLAY)
        
        st.markdown("---")
        
        if st.button("Save Settings", use_container_width=True):
            st.success("Settings saved!")
        
        st.markdown("---")
        st.markdown('<i class="fa-solid fa-chart-column"></i> App Statistics', unsafe_allow_html=True)
        st.info(f"""
        - Version: 2.1
        - Total Chats: {len(st.session_state.all_chats)}
        - Favorites: {len(st.session_state.favorites)}
        - Users: {st.session_state.username}
        - Saved Routes: {len(st.session_state.saved_routes)}
        """)

# -----------------------
# MAIN CONTENT AREA
# -----------------------
with main_col:
    # Ensure we have a conversation
    if not st.session_state.current_chat_id:
        cid = new_chat_id()
        st.session_state.current_chat_id = cid
        if not st.session_state.history:
            st.session_state.history = [{"role": "assistant", "content": "Hello! How can I assist you with travel today?"}]
        if not st.session_state.conversation_history:
            st.session_state.conversation_history = initialize_conversation()

    # Display current chat title
    current_title = st.session_state.chat_titles.get(st.session_state.current_chat_id, "New Conversation")
    st.markdown(f'<i class="fa-regular fa-comment"></i> {current_title}', unsafe_allow_html=True)

    # Chat messages
    for idx, message in enumerate(st.session_state.history[-NUMBER_OF_MESSAGES_TO_DISPLAY:]):
        role = message.get("role", "user")
        content = message.get("content", "")
        
        if role == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.write(content)
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("❤", key=f"fav_{idx}"):
                        if content.strip() not in st.session_state.favorites:
                            st.session_state.favorites.append(content.strip())
                            st.success("Added to favorites!")
                            save_current_chat()
                        else:
                            st.markdown(
    '<div style="background-color:#f8d7da; color:#721c24; padding:10px; border-radius:5px;">'
    '<i class="fa-solid fa-check"></i> Already in favorites.'
    '</div>',
    unsafe_allow_html=True
)
        else:
            with st.chat_message("user", avatar=""):
                st.write(content)

    # Chat input
    st.markdown("---")
    user_input = st.chat_input("Enter your message...")

    if user_input:
        user_message = user_input.strip()
        if user_message:
            st.session_state.history.append({"role": "user", "content": user_message})
            st.session_state.conversation_history.append({"role": "user", "content": user_message})
            
            try:
                with st.spinner("Thinking..."):
                    response = client.chat.completions.create(
                        model=DEFAULT_MODEL,
                        messages=st.session_state.conversation_history
                    )
                    assistant_reply = response.choices[0].message.content
            except OpenAIError as e:
                assistant_reply = f" Error: {e}"
                logging.error("Chatbot error: %s", e)
            
            st.session_state.history.append({"role": "assistant", "content": assistant_reply})
            st.session_state.conversation_history.append({"role": "assistant", "content": assistant_reply})
            
            save_current_chat()
            st.rerun()

    # Bottom controls
    st.markdown("---")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

    with col1:
        if st.button("Save", use_container_width=True):
            save_current_chat()
            st.success("Saved!")

    with col2:
        if st.button("Delete", use_container_width=True):
            st.session_state.history = []
            st.session_state.conversation_history = initialize_conversation()
            if st.session_state.current_chat_id:
                st.session_state.all_chats[st.session_state.current_chat_id] = {
                    "history": [],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "title": st.session_state.chat_titles.get(st.session_state.current_chat_id, "")
                }
            st.rerun()

    with col3:
        if st.button("Export", use_container_width=True):
            export_data = {
                "chat_id": st.session_state.current_chat_id,
                "title": current_title,
                "messages": st.session_state.history,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.download_button(
                "Export Chat",
                data=json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name=f"chat_{st.session_state.current_chat_id}.json",
                mime="application/json"
            )

    with col4:
        new_title = st.text_input("Rename chat", placeholder="Enter a name...", label_visibility="collapsed")
        if st.button("Rename", use_container_width=True):
            if new_title.strip():
                st.session_state.chat_titles[st.session_state.current_chat_id] = new_title.strip()
                save_current_chat()
                st.success(f"Renamed to: {new_title}")
                st.rerun()

# -----------------------
# RIGHT SIDEBAR - MAP
# -----------------------
if map_col is not None:
    with map_col:
        st.markdown('<i class="fa-solid fa-map-location"></i> Route Planning', unsafe_allow_html=True)
        
        # Route planning form
        with st.form("route_form"):
            start_loc = st.text_input(
                "Starting Point", 
                value=st.session_state.get("route_start", ""),
                placeholder="E.g., Ho Chi Minh City"
            )
            
            end_loc = st.text_input(
                "Destination", 
                value=st.session_state.get("route_end", ""),
                placeholder="E.g., Hanoi"
            )
            
            submit_route = st.form_submit_button("Find Route", use_container_width=True)
        
        # Xử lý submit hoặc trigger từ nút khác
        if submit_route or st.session_state.get("submit_route", False) or st.session_state.get("reload_trigger", False):
            st.session_state.submit_route = False
            st.session_state.reload_trigger = False
            st.session_state.route_start = start_loc
            st.session_state.route_end = end_loc
            
            with st.spinner("Calculating route..."):
                route_map, route_info = create_route_map(start_loc, end_loc)
                if route_map:
                    st.session_state.route_map = route_map
                    st.session_state.route_info = route_info
                else:
                    st.error(route_info)
        
        # Render map và thông tin tuyến (nếu có)
        if "route_map" in st.session_state and st.session_state.route_map:
            st.markdown(f"""
            <div class="route-info">
                {st.session_state.route_info}
            </div>
            """, unsafe_allow_html=True)
            
            st_folium(
                st.session_state.route_map, 
                width=None, height=400, key="route_map_display"
            )
            
            # Nút lưu tuyến
            if st.button("Save Route", use_container_width=True):
                route_data = {
                    "start": st.session_state.route_start,
                    "end": st.session_state.route_end,
                    "info": st.session_state.route_info,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                if route_data not in st.session_state.saved_routes:
                    st.session_state.saved_routes.append(route_data)
                    st.success("Route saved!")

        # Quick route templates
        st.markdown("---")
        st.markdown('<i class="fa-solid fa-location-pin"></i> Popular Routes', unsafe_allow_html=True)
        popular_routes = [
            {"name": "HCMC → Hanoi", "start": "Ho Chi Minh City", "end": "Hanoi"},
            {"name": "HCMC → Da Nang", "start": "Ho Chi Minh City", "end": "Da Nang"},
            {"name": "Hanoi → Ha Long", "start": "Hanoi", "end": "Ha Long"},
            {"name": "HCMC → Vung Tau", "start": "Ho Chi Minh City", "end": "Vung Tau"},
            {"name": "HCMC → Da Lat", "start": "Ho Chi Minh City", "end": "Da Lat"}
        ]
        for route in popular_routes:
            if st.button(f"{route['name']}", key=f"route_{route['name']}", use_container_width=True):
                st.session_state.route_start = route['start']
                st.session_state.route_end = route['end']
                st.session_state.submit_route = True

        # Saved routes
        if st.session_state.saved_routes:
            st.markdown("---")
            st.markdown('<i class="fa-solid fa-street-view"></i> Saved Routes', unsafe_allow_html=True)
            for i, saved in enumerate(st.session_state.saved_routes):
                with st.expander(f"{saved['start'][:15]}... → {saved['end'][:15]}..."):
                    st.write(f"**Start:** {saved['start']}")
                    st.write(f"**End:** {saved['end']}")
                    st.write(f"**{saved['info']}**")
                    st.caption(f"{saved['timestamp']}")
                    
                    col_a, col_b = st.columns(2)
                    if col_a.button("Reload", key=f"reload_route_{i}"):
                        st.session_state.route_start = saved['start']
                        st.session_state.route_end = saved['end']
                        st.session_state.reload_trigger = True
                    
                    if col_b.button("Delete", key=f"delete_route_{i}"):
                        st.session_state.saved_routes.pop(i)
                        st.experimental_rerun = False  # Không cần nữa, reload_trigger sẽ xử lý

        # Map info
        st.markdown("---")
        st.info("""
        💡 **Instructions:**
        - Enter location names (e.g., Ho Chi Minh City, Hanoi)
        - Click "Find Route"
        - View map and detailed information
        - Save favorite routes
        """)
