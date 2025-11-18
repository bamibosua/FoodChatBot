# tourism_chatbot_app.py
import logging
import json
import base64
import time
from datetime import datetime
from typing import List, Dict
from streamlit_folium import st_folium

import streamlit as st
from PIL import Image, ImageEnhance
from openai import OpenAI, OpenAIError

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
    return datetime.utcnow().strftime("chat_%Y%m%d%H%M%S%f")

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
    assistant_message = "Xin chào! Tôi là trợ lý du lịch của bạn. Tôi có thể giúp bạn tìm địa điểm tham quan, nhà hàng, khách sạn và lên kế hoạch cho chuyến đi. Bạn cần tôi giúp gì?"
    return [
        {"role": "system", "content": "You are a helpful tourism assistant. Provide recommendations for restaurants, hotels, attractions, and travel planning."},
        {"role": "assistant", "content": assistant_message}
    ]

def get_chat_preview(history):
    """Get a preview of the chat for display."""
    if not history:
        return "Empty chat"
    for msg in history:
        if msg.get("role") == "user":
            preview = msg.get("content", "")[:50]
            return preview + "..." if len(msg.get("content", "")) > 50 else preview
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
        st.session_state.route_start = "Thành phố Hồ Chí Minh, Việt Nam"
    if "route_end" not in st.session_state:
        st.session_state.route_end = "Hà Nội, Việt Nam"
    if "saved_routes" not in st.session_state:
        st.session_state.saved_routes = []

initialize_session_state()

# -----------------------
# PAGE CONFIG + THEME
# -----------------------
st.set_page_config(
    page_title="Tourism Chatbot 🌍",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS styling
st.markdown("""
<style>
    /* Main background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #ecf0f1;
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
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
        color: white;
        text-align: center;
        margin: 10px 0;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------
# LOGIN LOGIC
# -----------------------
def show_login_page():
    st.markdown("""
    <div class="login-card">
        <h2 style="text-align: center; color: #667eea;">🔐 Đăng nhập</h2>
        <p style="text-align: center; color: #666;">Vui lòng đăng nhập để sử dụng Tourism Chatbot</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("👤 Tên đăng nhập", placeholder="Nhập tên đăng nhập")
            password = st.text_input("🔒 Mật khẩu", type="password", placeholder="Nhập mật khẩu")
            
            col_a, col_b = st.columns(2)
            login_btn = col_a.form_submit_button("🚀 Đăng nhập", use_container_width=True)
            register_btn = col_b.form_submit_button("📝 Đăng ký", use_container_width=True)
            
            if login_btn:
                if username and password:
                    if username == "admin" and password == "admin":
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("✅ Đăng nhập thành công!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Sai tên đăng nhập hoặc mật khẩu!")
                else:
                    st.warning("⚠️ Vui lòng nhập đầy đủ thông tin!")
            
            if register_btn:
                if username and password:
                    st.success("✅ Đăng ký thành công! Vui lòng đăng nhập.")
                else:
                    st.warning("⚠️ Vui lòng nhập đầy đủ thông tin!")
        
        st.info("💡 Demo: username='admin', password='admin'")

# Check login status
if not st.session_state.logged_in:
    show_login_page()
    st.stop()

# Header
st.markdown("""
<div class="custom-header">
    <h1>🌍 Tourism Chatbot</h1>
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
    # User profile section
    st.markdown(f"""
    <div class="user-badge">
        👤 {st.session_state.username}
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
    
    st.markdown("---")
    
    # Toggle map sidebar
    if st.checkbox("🗺️ Hiện bản đồ", value=st.session_state.show_map_sidebar):
        st.session_state.show_map_sidebar = True
    else:
        st.session_state.show_map_sidebar = False
    
    st.markdown("---")
    st.markdown("# 🎯 Menu")
    st.markdown("---")
    
    # Menu with icons
    menu = st.radio(
        "Chọn chức năng:",
        ["💬 Chat mới", "📚 Lịch sử", "⭐ Yêu thích", "⚙️ Cài đặt"],
        index=0
    )
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("### 📊 Thống kê")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Cuộc trò chuyện", len(st.session_state.all_chats))
    with col2:
        st.metric("Yêu thích", len(st.session_state.favorites))
    
    st.markdown("---")

# -----------------------
# MENU: NEW CHAT
# -----------------------
if menu == "💬 Chat mới":
    with st.sidebar:
        st.markdown("### 🆕 Bắt đầu cuộc trò chuyện mới")
        
        if st.button("➕ Tạo chat mới", use_container_width=True):
            if st.session_state.current_chat_id:
                save_current_chat()
            
            cid = new_chat_id()
            st.session_state.current_chat_id = cid
            st.session_state.history = [{"role": "assistant", "content": "Xin chào! Tôi là trợ lý du lịch. Tôi có thể giúp bạn tìm nhà hàng, khách sạn, địa điểm tham quan hoặc lên kế hoạch cho chuyến đi. Bạn muốn tôi giúp gì?"}]
            st.session_state.conversation_history = initialize_conversation()
            st.rerun()
        
        st.markdown("---")
        st.info("💡 Mẹo: Nhấn nút ⭐ dưới tin nhắn bot để lưu vào mục yêu thích!")

# -----------------------
# MENU: CONVERSATION HISTORY
# -----------------------
elif menu == "📚 Lịch sử":
    with st.sidebar:
        st.markdown("### 💬 Lịch sử cuộc trò chuyện")
        
        if st.session_state.all_chats:
            search_term = st.text_input("🔍 Tìm kiếm cuộc trò chuyện", "")
            
            ordered = sorted(st.session_state.all_chats.items(), key=lambda kv: kv[1].get("timestamp", ""), reverse=True)
            
            for chat_id, chat_data in ordered:
                history = chat_data.get("history", [])
                timestamp = chat_data.get("timestamp", "")
                title = chat_data.get("title", chat_id)
                preview = get_chat_preview(history)
                
                if search_term and search_term.lower() not in preview.lower() and search_term.lower() not in title.lower():
                    continue
                
                with st.expander(f"📝 {title[:30]}..."):
                    st.caption(f"🕒 {timestamp}")
                    st.write(f"💬 {preview}")
                    
                    col1, col2 = st.columns(2)
                    if col1.button("📂 Mở", key=f"load_{chat_id}"):
                        if st.session_state.current_chat_id:
                            save_current_chat()
                        st.session_state.current_chat_id = chat_id
                        st.session_state.history = history.copy()
                        st.session_state.conversation_history = initialize_conversation()
                        st.rerun()
                    
                    if col2.button("🗑️ Xóa", key=f"del_{chat_id}"):
                        st.session_state.all_chats.pop(chat_id, None)
                        st.session_state.chat_titles.pop(chat_id, None)
                        if st.session_state.current_chat_id == chat_id:
                            st.session_state.current_chat_id = None
                            st.session_state.history = []
                            st.session_state.conversation_history = []
                        st.rerun()
        else:
            st.info("📭 Chưa có cuộc trò chuyện nào được lưu.")

# -----------------------
# MENU: FAVORITES
# -----------------------
elif menu == "⭐ Yêu thích":
    with st.sidebar:
        st.markdown("### ⭐ Danh sách yêu thích")
        
        if st.session_state.favorites:
            fav_search = st.text_input("🔍 Tìm trong yêu thích", "")
            
            for i, fav in enumerate(st.session_state.favorites, start=1):
                if fav_search and fav_search.lower() not in fav.lower():
                    continue
                
                with st.expander(f"⭐ Mục {i}"):
                    st.write(fav[:100] + "..." if len(fav) > 100 else fav)
                    if st.button("🗑️ Xóa", key=f"remove_fav_{i}"):
                        st.session_state.favorites.remove(fav)
                        st.rerun()
            
            st.markdown("---")
            if st.button("🗑️ Xóa tất cả yêu thích", use_container_width=True):
                st.session_state.favorites = []
                st.rerun()
        else:
            st.info("📭 Chưa có mục yêu thích nào.")

# -----------------------
# MENU: SETTINGS
# -----------------------
elif menu == "⚙️ Cài đặt":
    with st.sidebar:
        st.markdown("### ⚙️ Cài đặt")
        
        model_option = st.selectbox(
            "Chọn mô hình AI:",
            ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            index=0
        )
        
        theme = st.selectbox(
            "Chủ đề màu sắc:",
            ["Tím (mặc định)", "Xanh dương", "Xanh lá"],
            index=0
        )
        
        msg_count = st.slider("Số tin nhắn hiển thị:", 10, 100, NUMBER_OF_MESSAGES_TO_DISPLAY)
        
        st.markdown("---")
        
        if st.button("💾 Lưu cài đặt", use_container_width=True):
            st.success("✅ Đã lưu cài đặt!")
        
        st.markdown("---")
        st.markdown("### 📊 Thông tin ứng dụng")
        st.info(f"""
        - Phiên bản: 2.1
        - Mô hình: {model_option}
        - Tổng chat: {len(st.session_state.all_chats)}
        - Yêu thích: {len(st.session_state.favorites)}
        - Người dùng: {st.session_state.username}
        - Tuyến đường đã lưu: {len(st.session_state.saved_routes)}
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
            st.session_state.history = [{"role": "assistant", "content": "Xin chào! Tôi có thể giúp bạn về du lịch như thế nào?"}]
        if not st.session_state.conversation_history:
            st.session_state.conversation_history = initialize_conversation()

    # Display current chat title
    current_title = st.session_state.chat_titles.get(st.session_state.current_chat_id, "Cuộc trò chuyện mới")
    st.markdown(f"### 💬 {current_title}")

    # Chat messages
    for idx, message in enumerate(st.session_state.history[-NUMBER_OF_MESSAGES_TO_DISPLAY:]):
        role = message.get("role", "user")
        content = message.get("content", "")
        
        if role == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.write(content)
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("⭐", key=f"fav_{idx}"):
                        if content.strip() not in st.session_state.favorites:
                            st.session_state.favorites.append(content.strip())
                            st.success("✅ Đã thêm vào yêu thích!")
                            save_current_chat()
                        else:
                            st.info("ℹ️ Đã có trong yêu thích.")
        else:
            with st.chat_message("user", avatar="👤"):
                st.write(content)

    # Chat input
    st.markdown("---")
    user_input = st.chat_input("💬 Nhập tin nhắn của bạn...")

    if user_input:
        user_message = user_input.strip()
        if user_message:
            st.session_state.history.append({"role": "user", "content": user_message})
            st.session_state.conversation_history.append({"role": "user", "content": user_message})
            
            try:
                with st.spinner("🤔 Đang suy nghĩ..."):
                    response = client.chat.completions.create(
                        model=DEFAULT_MODEL,
                        messages=st.session_state.conversation_history
                    )
                    assistant_reply = response.choices[0].message.content
            except OpenAIError as e:
                assistant_reply = f"❌ Lỗi: {e}"
                logging.error("OpenAIError: %s", e)
            
            st.session_state.history.append({"role": "assistant", "content": assistant_reply})
            st.session_state.conversation_history.append({"role": "assistant", "content": assistant_reply})
            
            save_current_chat()
            st.rerun()

    # Bottom controls
    st.markdown("---")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

    with col1:
        if st.button("💾 Lưu", use_container_width=True):
            save_current_chat()
            st.success("✅ Đã lưu!")

    with col2:
        if st.button("🗑️ Xóa", use_container_width=True):
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
        if st.button("📤 Xuất", use_container_width=True):
            export_data = {
                "chat_id": st.session_state.current_chat_id,
                "title": current_title,
                "messages": st.session_state.history,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.download_button(
                "📥 Tải xuống JSON",
                data=json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name=f"chat_{st.session_state.current_chat_id}.json",
                mime="application/json"
            )

    with col4:
        new_title = st.text_input("✏️ Đặt tên chat", placeholder="Nhập tên...", label_visibility="collapsed")
        if st.button("✅ Đặt tên", use_container_width=True):
            if new_title.strip():
                st.session_state.chat_titles[st.session_state.current_chat_id] = new_title.strip()
                save_current_chat()
                st.success(f"✅ Đã đổi tên: {new_title}")
                st.rerun()

# -----------------------
# RIGHT SIDEBAR - MAP
# -----------------------
if map_col is not None:
    with map_col:
        st.markdown("### 🗺️ Lập tuyến đường")
        
        # Route planning form
        with st.form("route_form"):
            start_loc = st.text_input(
                "📍 Điểm đi", 
                value=st.session_state.get("route_start", ""),
                placeholder="VD: Thành phố Hồ Chí Minh"
            )
            
            end_loc = st.text_input(
                "🏁 Điểm đến", 
                value=st.session_state.get("route_end", ""),
                placeholder="VD: Hà Nội"
            )
            
            submit_route = st.form_submit_button("🚗 Tìm tuyến đường", use_container_width=True)
        
        # Xử lý submit hoặc trigger từ nút khác
        if submit_route or st.session_state.get("submit_route", False) or st.session_state.get("reload_trigger", False):
            st.session_state.submit_route = False
            st.session_state.reload_trigger = False
            st.session_state.route_start = start_loc
            st.session_state.route_end = end_loc
            
            with st.spinner("🔍 Đang tìm tuyến đường..."):
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
            if st.button("💾 Lưu tuyến đường", use_container_width=True):
                route_data = {
                    "start": st.session_state.route_start,
                    "end": st.session_state.route_end,
                    "info": st.session_state.route_info,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                if route_data not in st.session_state.saved_routes:
                    st.session_state.saved_routes.append(route_data)
                    st.success("✅ Đã lưu tuyến đường!")

        # Quick route templates
        st.markdown("---")
        st.markdown("### 🚀 Tuyến phổ biến")
        popular_routes = [
            {"name": "TPHCM → Hà Nội", "start": "Thành phố Hồ Chí Minh", "end": "Hà Nội"},
            {"name": "TPHCM → Đà Nẵng", "start": "Thành phố Hồ Chí Minh", "end": "Đà Nẵng"},
            {"name": "Hà Nội → Hạ Long", "start": "Hà Nội", "end": "Hạ Long"},
            {"name": "TPHCM → Vũng Tàu", "start": "Thành phố Hồ Chí Minh", "end": "Vũng Tàu"},
            {"name": "TPHCM → Đà Lạt", "start": "Thành phố Hồ Chí Minh", "end": "Đà Lạt"}
        ]
        for route in popular_routes:
            if st.button(f"🛣️ {route['name']}", key=f"route_{route['name']}", use_container_width=True):
                st.session_state.route_start = route['start']
                st.session_state.route_end = route['end']
                st.session_state.submit_route = True

        # Saved routes
        if st.session_state.saved_routes:
            st.markdown("---")
            st.markdown("### 📁 Tuyến đã lưu")
            for i, saved in enumerate(st.session_state.saved_routes):
                with st.expander(f"🗺️ {saved['start'][:15]}... → {saved['end'][:15]}..."):
                    st.write(f"**Điểm đi:** {saved['start']}")
                    st.write(f"**Điểm đến:** {saved['end']}")
                    st.write(f"**{saved['info']}**")
                    st.caption(f"🕒 {saved['timestamp']}")
                    
                    col_a, col_b = st.columns(2)
                    if col_a.button("🔄 Tải lại", key=f"reload_route_{i}"):
                        st.session_state.route_start = saved['start']
                        st.session_state.route_end = saved['end']
                        st.session_state.reload_trigger = True
                    
                    if col_b.button("🗑️ Xóa", key=f"delete_route_{i}"):
                        st.session_state.saved_routes.pop(i)
                        st.experimental_rerun = False  # Không cần nữa, reload_trigger sẽ xử lý

        # Map info
        st.markdown("---")
        st.info("""
        💡 **Hướng dẫn:**
        - Nhập tên địa điểm (VD: Thành phố Hồ Chí Minh)
        - Click "Tìm tuyến đường"
        - Xem bản đồ và thông tin chi tiết
        - Lưu tuyến yêu thích
        """)
