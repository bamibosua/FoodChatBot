# utils/helpers.py
import streamlit as st
import base64
from datetime import datetime

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

def new_chat_id():
    return datetime.now().strftime("chat_%Y%m%d%H%M%S%f")

def save_current_chat():
    cid = st.session_state.current_chat_id
    if cid and st.session_state.get('logged_in', False):
        st.session_state.all_chats[cid] = {
            "history": st.session_state.history.copy(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": st.session_state.chat_titles.get(cid, cid)
        }

def initialize_conversation():
    return [
        {"role": "system", "content": "You are a helpful tourism assistant. Provide recommendations for restaurants"},
        {"role": "assistant", "content": "Xin chào! Tôi là dân sì gòn gốc, bạn muốn ăn gì? Tôi dẫn bạn dạt khắp sì gòn."}
    ]

def get_chat_preview(history):
    if not history:
        return "Empty chat"
    for msg in history:
        if msg.get("role") == "user":
            preview = msg.get("content", "")[:50]
            return preview + "..." if len(msg.get("content", "")) > 50 else preview
    return "New conversation"

    # utils/helpers.py
import base64
import logging
from datetime import datetime
from typing import List, Dict

def img_to_base64(image_path: str):
    """Convert image to base64 string"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        logging.debug(f"Could not load image {image_path}: {e}")
        return None

def get_base64_image(image_path):
    """Get base64 encoded image"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def load_image_base64(path):
    """Load image as base64"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def new_chat_id() -> str:
    """Generate a new chat id using timestamp for uniqueness."""
    return datetime.now().strftime("chat_%Y%m%d%H%M%S%f")

def save_current_chat():
    """Save the current open chat history into all_chats."""
    import streamlit as st
    cid = st.session_state.current_chat_id
    if cid and st.session_state.get('logged_in', False):
        st.session_state.all_chats[cid] = {
            "history": st.session_state.history.copy(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": st.session_state.chat_titles.get(cid, cid)
        }
        logging.info(f"Saved chat {cid} with {len(st.session_state.history)} messages.")

def get_chat_preview(history):
    """Lấy đoạn xem trước của cuộc trò chuyện"""
    if not history:
        return "Empty chat"
    for msg in history:
        if msg.get("role") == "user":
            preview = msg.get("content", "")[:50]
            return preview + "..." if len(msg.get("content", "")) > 50 else preview
    return "New conversation"

def initialize_conversation() -> List[Dict]: 
    """Khởi tạo cuộc trò chuyện với tin nhắn ban đầu"""
    assistant_message = "Xin chào! Tôi là dân sì gòn gốc, bạn muốn ăn gì? Tôi dẫn bạn dạt khắp sì gòn."
    return [
        {"role": "system", "content": "You are a helpful tourism assistant. Provide recommendations for restaurants"},
    ]