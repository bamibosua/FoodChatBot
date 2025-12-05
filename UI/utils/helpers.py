# utils/helpers.py
import streamlit as st
import base64
from datetime import datetime

def food_image():
    img_base64 = get_base64_image("UI/imgs/food3.jpg")
    st.markdown(
        f'''
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 100%;
        ">
            <img src="data:image/jpeg;base64,{img_base64}" 
                 style="
                    width: 90%;
                    height: 100%;
                    object-fit: contain;        /* Phủ đầy khung mà vẫn giữ tỉ lệ */
                    border-radius: 20px;
                 ">
        </div>
        ''',
        unsafe_allow_html=True
    )

def title_form():
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

def background_image():
    image_path = "UI/imgs/background2.png"
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
        </style>
        '''
    st.markdown(css, unsafe_allow_html=True)

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