# utils/helpers.py
import streamlit as st
import json
import os
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

def apply_header_sidebar_styles():
     st.markdown(f"""
        <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 10px; 
                margin-bottom: 20px; 
                text-align: center;"
                font-family: Times New Roman, serif;
                >
            <h2 style="color: white; margin: 0;"> Hello, {st.session_state.username}</h2>
        </div>
        """, unsafe_allow_html=True)

# Hàm lưu lịch sử chat vào file
# username: tên user
# all_chats: dict chứa toàn bộ lịch sử chat
# Trả về True nếu lưu thành công, False nếu lỗi
def save_chat_history_to_file(username, all_chats):
    """Lưu toàn bộ lịch sử chat của user vào file JSON"""
    try:
        filename = f"chat_history_{username}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_chats, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu: {e}")
        return False

# Hàm load lịch sử chat từ file
# username: tên user
# Trả về dict chứa toàn bộ lịch sử chat hoặc rỗng nếu lỗi
def load_chat_history_from_file(username):
    """Load lịch sử chat của user từ file JSON"""
    try:
        filename = f"chat_history_{username}.json"
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        st.error(f"Loading Error: {e}")
        return {}

# Hàm tự động lưu chat hiện tại
def save_current_chat():
    """Lưu chat hiện tại vào all_chats và file"""
    if st.session_state.current_chat_id and st.session_state.history:
        st.session_state.all_chats[st.session_state.current_chat_id] = {
            "history": st.session_state.history.copy(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": get_chat_title(st.session_state.history)
        }
        # Tự động lưu vào file
        save_chat_history_to_file(st.session_state.username, st.session_state.all_chats)

# Hàm tạo ID chat mới
def new_chat_id():
    """Tạo ID duy nhất cho chat mới"""
    return f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Hàm lấy tiêu đề chat
def get_chat_title(history):
    """Lấy tiêu đề từ tin nhắn đầu tiên của user"""
    for msg in history:
        if msg["role"] == "user":
            content = msg["content"]
            return content[:50] if len(content) > 50 else content
    return "Untitled Chat"

# Hàm lấy preview chat
def get_chat_preview(history):
    """Lấy preview từ lịch sử chat"""
    if not history:
        return "Empty chat"
    for msg in history:
        if msg["role"] == "user":
            content = msg["content"]
            return content[:100] if len(content) > 100 else content
    return "No messages"

# Hàm khởi tạo conversation
def initialize_conversation(chat_id, username):
    """Tự động load conversation từ database (file JSON)."""
    
    filepath = f"chat_history_{username}.json"
    
    # Nếu file không tồn tại → trả về danh sách trống
    if not os.path.exists(filepath):
        return []
    
    # Load file
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Kiểm tra ID chat có trong database không
    if chat_id not in data:
        return []
    
    # Trả về history của chat
    return data[chat_id].get("history", [])

def load_user_chats(username):
    filepath = f"chat_history_{username}.json"
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
