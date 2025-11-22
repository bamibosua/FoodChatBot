# config/settings.py
import streamlit as st
import logging
from openai import OpenAI
from firebase_admin import credentials, firestore
import firebase_admin
import pyrebase

logging.basicConfig(level=logging.INFO)

# ========================
# FIREBASE
# ========================
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


# ========================
# OPENAI CLIENT – QUAN TRỌNG: PHẢI CÓ DÒNG NÀY!
# ========================
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "your-openai-api-key")  # Lấy từ secrets.toml
if not OPENAI_API_KEY or OPENAI_API_KEY == "your-openai-api-key":
    st.error("Please set your OpenAI API key in Streamlit secrets!")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)  # ← DÒNG NÀY BỊ THIẾU!!!

# ========================
# CONSTANTS
# ========================
NUMBER_OF_MESSAGES_TO_DISPLAY = 50
DEFAULT_MODEL = "gpt-4o-mini"

# Application settings
APP_TITLE = "Food Chatbot"
APP_ICON = "🍽️"
APP_VERSION = "2.1"
LAYOUT = "wide"

# Chat settings
NUMBER_OF_MESSAGES_TO_DISPLAY = 50
DEFAULT_MODEL = "gpt-4o-mini"

# Logging configuration
LOG_LEVEL = logging.INFO

# UI Constants
POPULAR_ROUTES = [
    {"name": "HCMC → Hanoi", "start": "Ho Chi Minh City", "end": "Hanoi"},
    {"name": "HCMC → Da Nang", "start": "Ho Chi Minh City", "end": "Da Nang"},
    {"name": "Hanoi → Ha Long", "start": "Hanoi", "end": "Ha Long"},
    {"name": "HCMC → Vung Tau", "start": "Ho Chi Minh City", "end": "Vung Tau"},
    {"name": "HCMC → Da Lat", "start": "Ho Chi Minh City", "end": "Da Lat"}
]

# Default locations
DEFAULT_START_LOCATION = "Quận 2, Thành phố Hồ Chí Minh, Việt Nam"
DEFAULT_END_LOCATION = "Quận 1, Thành phố Hồ Chí Minh, Việt Nam"

# Menu options
MENU_OPTIONS = ["New Chat!", "History", "Favorites", "Settings"]

# Theme options
THEME_OPTIONS = [
    "Light Yellow (default)", 
    "Blue", 
    "Green", 
    "Orange", 
    "Pink", 
    "Purple"
]

# ========================
# CONSTANTS
# ========================
OPENAI_API_KEY = "your-openai-api-key"  # hoặc lấy từ secrets
NUMBER_OF_MESSAGES_TO_DISPLAY = 50
DEFAULT_MODEL = "gpt-4o-mini"