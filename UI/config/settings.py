# config/settings.py
import streamlit as st
import logging
from firebase_admin import credentials, firestore
import firebase_admin
import pyrebase

logging.basicConfig(level=logging.INFO)

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


#Application settings
APP_TITLE = "Food Chatbot"
APP_ICON = "🍽️"
APP_VERSION = "2.1"
LAYOUT = "wide"

#Chat settings
NUMBER_OF_MESSAGES_TO_DISPLAY = 50


#Logging configuration
LOG_LEVEL = logging.INFO
