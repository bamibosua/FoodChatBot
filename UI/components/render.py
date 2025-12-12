import streamlit as st
import json
import os
import base64
from .logic import parse_user_input, process_logic, generate_reply

from streamlit_folium import st_folium
import folium
from .map_utils import create_multi_destination_map

from UI.config.settings import NUMBER_OF_MESSAGES_TO_DISPLAY
from UI.utils.helpers import save_current_chat, new_chat_id, initialize_conversation

import streamlit.components.v1 as components

def init_food_state():
    defaults = {
        "history": [],
        "conversation_history": initialize_conversation(st.session_state.current_chat_id, st.session_state.username),
        "final_data": {"location": None, "city": None, "foods": [], "budget": None},
        "chat_titles": {},
        "favorites": [],
        "pending_user_input": None,
        "filtered_restaurants": {},
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = new_chat_id()

    if len(st.session_state.history) == 0:
        welcome = (
            "Hello! I'm your food assistant!\n"
            "Please enter your preferred district in Ho Chi Minh City, "
            "your taste or food you want, and your budget (VND)."
        )
        st.session_state.history.append({"role": "assistant", "content": welcome})
        st.session_state.conversation_history.append(
            {"role": "assistant", "content": welcome}
        )
    
    if "final_data" not in st.session_state:
        st.session_state.final_data = {
            "location": None,
            "city": None,
            "foods": [],
            "budget": None,
        }
    if "city" not in st.session_state:
        st.session_state.city = None
        
def init_map_session_state():
    defaults = {
        "current_location": "",
        "multi_map": None,
        "multi_info": {},
        "show_default_map": True,
        "filtered_restaurants": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# def render_messages():
#     """Render messages với gradient bubbles + AUTO SCROLL sử dụng st.container()"""
    
#     messages = st.session_state.history[-NUMBER_OF_MESSAGES_TO_DISPLAY:]
    
#     # CSS cho chat bubbles
#     st.markdown("""
#     <style>
#     .chat-container {
#         max-height: 450px;
#         overflow-y: auto;
#         padding: 1rem;
#         scroll-behavior: smooth;
#     }
    
#     .chat-message {
#         padding: 1rem;
#         border-radius: 0.8rem;
#         margin-bottom: 1rem;
#         display: flex;
#         align-items: flex-start;
#         gap: 0.8rem;
#         animation: fadeIn 0.3s ease-in;
#     }
    
#     @keyframes fadeIn {
#         from { opacity: 0; transform: translateY(10px); }
#         to { opacity: 1; transform: translateY(0); }
#     }
    
#     .chat-message.bot {
#         background: white;
#         margin-right: 20%;
#         border-bottom-left-radius: 0.2rem;
#         box-shadow: 0 1px 3px rgba(0,0,0,0.1);
#     }
    
#     .chat-message.user {
#         background: #CEE6F2;
#         margin-left: 20%;
#         flex-direction: row-reverse;
#         border-bottom-right-radius: 0.2rem;
#         box-shadow: 0 1px 3px rgba(0,0,0,0.1);
#     }
    
#     .chat-avatar {
#         width: 40px;
#         height: 40px;
#         border-radius: 50%;
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         font-size: 1.5rem;
#         flex-shrink: 0;
#     }
    
#     .chat-content {
#         flex: 1;
#         color: black;
#         line-height: 1.6;
#         word-wrap: break-word;
#     }
    
#     .chat-role {
#         font-size: 0.75rem;
#         font-weight: 600;
#         text-transform: uppercase;
#         letter-spacing: 0.5px;
#         margin-bottom: 0.3rem;
#         opacity: 0.7;
#         color: #555;
#     }
    
#     /* Ẩn scrollbar nhưng vẫn scroll được */
#     .chat-container::-webkit-scrollbar {
#         width: 6px;
#     }
    
#     .chat-container::-webkit-scrollbar-track {
#         background: #f1f1f1;
#         border-radius: 10px;
#     }
    
#     .chat-container::-webkit-scrollbar-thumb {
#         background: #888;
#         border-radius: 10px;
#     }
    
#     .chat-container::-webkit-scrollbar-thumb:hover {
#         background: #555;
#     }
#     </style>
#     """, unsafe_allow_html=True)
    
#     # Tạo container cho chat messages
#     chat_container = st.container(height=450)
    
#     with chat_container:
#         # Render từng message
#         for msg in messages:
#             role_class = "bot" if msg["role"] == "assistant" else "user"
#             avatar = "🤖" if msg["role"] == "assistant" else "👨‍🚀"
#             role_label = "ASSISTANT" if msg["role"] == "assistant" else "YOU"
#             content = msg["content"].replace("\n", "<br>")
            
#             st.markdown(f"""
#             <div class="chat-message {role_class}">
#                 <div class="chat-avatar">{avatar}</div>
#                 <div class="chat-content">
#                     <div class="chat-role">{role_label}</div>
#                     <div>{content}</div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)

def render_messages():
    """Render messages với gradient bubbles + AUTO SCROLL"""
    import streamlit.components.v1 as components
    
    # CSS + HTML + JavaScript trong một component
    messages = st.session_state.history[-NUMBER_OF_MESSAGES_TO_DISPLAY:]
    
    # Build HTML
    html_content = """
    <style>
    .chat-container {
        max-height: 450px;
        overflow-y: auto;
        padding: 1rem;
        scroll-behavior: smooth;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
        gap: 0.8rem;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    /* chinh mau nen tin nhan bot */
    .chat-message.bot {
        background: white;
        margin-right: 20%;
        border-bottom-left-radius: 0.2rem;
    }
    /* chinh mau nen tin nhan nguoi dung */
    .chat-message.user {
        background: #CEE6F2;
        margin-left: 20%;
        flex-direction: row-reverse;
        border-bottom-right-radius: 0.2rem;
    }
    
    .chat-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
        background: rgba(255, 255, 255, 0.2);
    }
    
    .chat-content {
        flex: 1;
        color: black;
        line-height: 1.6;
        word-wrap: break-word;
    }
    
    .chat-role {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.3rem;
        opacity: 0.9;
    }
    </style>
    
    <div class="chat-container" id="chatContainer">
    """
    
    # Add messages
    for msg in messages:
        role_class = "bot" if msg["role"] == "assistant" else "user"
        avatar = "🤖" if msg["role"] == "assistant" else "👨‍🚀"
        role_label = "ASSISTANT" if msg["role"] == "assistant" else "YOU"
        content = msg["content"].replace("\n", "<br>")
        
        html_content += f"""
        <div class="chat-message {role_class}">
            <div class="chat-avatar">{avatar}</div>
            <div class="chat-content">
                <div class="chat-role">{role_label}</div>
                {content}
            </div>
        </div>
        """
    
    html_content += """
        <div id="bottom"></div>
    </div>
    
    <script>
    // Auto scroll to bottom
    function scrollToBottom() {
        const container = document.getElementById('chatContainer');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }
    
    // Scroll on load
    window.addEventListener('load', scrollToBottom);
    
    // Scroll after a short delay (for dynamic content)
    setTimeout(scrollToBottom, 100);
    setTimeout(scrollToBottom, 300);
    setTimeout(scrollToBottom, 500);
    </script>
    """
    
    # Render with iframe
    components.html(html_content, height=490, scrolling=False)

def render_main_chat():
        
    init_food_state()

    current_title = st.session_state.chat_titles.get(
        st.session_state.current_chat_id, "New Chat"
    )
    st.markdown(f"{current_title}")

    render_messages()

    # XỬ LÝ PENDING INPUT TRƯỚC KHI RENDER
    if st.session_state.pending_user_input:
        user_msg = st.session_state.pending_user_input
        st.session_state.pending_user_input = None

        # 1️.parse
        parsed_data, original_lang = parse_user_input(user_msg)

        # 2️.xử lý logic (chỉ chạy 1 lần)
        processed_result = process_logic(
            parsed_data,
            original_lang,
            st.session_state.final_data,
            st.session_state.city
        )

        # lưu kết quả vào session_state
        st.session_state.processed_result = processed_result
        st.session_state.original_lang_for_result = original_lang
        st.session_state.filtered_restaurants = processed_result.get("processed_data", {})

        # 3️⃣ tạo output bot_reply
        bot_reply = generate_reply(processed_result, original_lang)

        # ✅ LƯU BOT REPLY
        st.session_state.history.append({"role": "assistant", "content": bot_reply})
        st.session_state.conversation_history.append(
            {"role": "assistant", "content": bot_reply}
        )
        
        # Reset final_data
        for key in st.session_state.final_data:
            if key in ["foods", "taste"]:
                st.session_state.final_data[key] = []
            else:
                st.session_state.final_data[key] = None
        
        save_current_chat()
        # KHÔNG RERUN Ở ĐÂY - để render_messages() hiển thị đủ cả user + bot
    
    # SAU KHI XỬ LÝ XONG, MỚI RENDER MESSAGES
    # render_messages()
        
    # NHẬN INPUT MỚI
    user_input = st.chat_input("Type your message...")

    if user_input:
        # ✅ LƯU USER MESSAGE
        st.session_state.history.append({"role": "user", "content": user_input})
        st.session_state.conversation_history.append(
            {"role": "user", "content": user_input}
        )
        st.session_state.pending_user_input = user_input
        st.rerun()
    # Rename chat
    # new_name = st.text_input("Rename", placeholder="New name", label_visibility="collapsed")
    # if st.button("Rename") and new_name.strip():
    #     st.session_state.chat_titles[st.session_state.current_chat_id] = new_name.strip()
    #     st.success("Renamed!")
    #     st.rerun()
            
def render_map_sidebar(map_col=None, restaurant_places=None):
    init_map_session_state()
    if map_col is None:
        return

    with map_col:
        st.markdown("## 🗺️ Route")
        
        RESTAURANT_PLACES = restaurant_places or st.session_state.get("filtered_restaurants", {})
        
        # ---------------- INPUT FORM ----------------
        with st.form("location_form", clear_on_submit=False):
            st.text_input(
                "📍 Your Location",
                key="current_location_input",
                placeholder="E.g., District 1, Ho Chi Minh City"
            )
            loc = st.session_state.current_location_input
            submit = st.form_submit_button("🚗 Show Routes", use_container_width=True)

        # ---------------- SUBMIT ----------------
        if submit:
            if not loc.strip():
                st.warning("⚠️ Please enter your location!")
            else:
                st.session_state.current_location = loc.strip()  # ← FIX: dùng biến loc

                with st.spinner("🔄 Creating routes..."):
                    if not RESTAURANT_PLACES:
                        st.error("❌ No restaurants to route to!")
                        st.session_state.multi_map = None
                        st.session_state.multi_info = {}
                        st.session_state.show_default_map = True
                    else:
                        m, info = create_multi_destination_map(loc, RESTAURANT_PLACES)
                        if m and info and not info.get('error'):
                            st.session_state.multi_map = m
                            st.session_state.multi_info = info
                            st.session_state.show_default_map = False
                            st.success(f"✅ Routes created to {len(info)} restaurants!")
                        else:
                            st.error(f"❌ Failed to create routes: {info.get('error', 'Unknown error')}")
                            st.session_state.multi_map = None
                            st.session_state.multi_info = {}
                            st.session_state.show_default_map = True

        # =======================================================
        #          LUÔN HIỂN THỊ MAP - FIX LOGIC
        # =======================================================
        st.markdown("### 🗺️ Map View")

        # ✅ FIX: Kiểm tra route map TRƯỚC
        if st.session_state.multi_map and not st.session_state.get("show_default_map", True):
            st_folium(
                st.session_state.multi_map,
                height=450,
                returned_objects=[],
                key="map_route"
            )

        # Nếu CHƯA có route nhưng CÓ RESTAURANTS → show markers only
        elif RESTAURANT_PLACES:
            m = folium.Map(location=[10.776, 106.7], zoom_start=12)
            for r in RESTAURANT_PLACES:
                if r.get("lat") and r.get("lng"):  # ← FIX: Kiểm tra tọa độ
                    folium.Marker(
                        [r["lat"], r["lng"]],
                        popup=r.get("name", "Restaurant"),
                        icon=folium.Icon(color='blue', icon='utensils', prefix='fa')
                    ).add_to(m)

            st_folium(m, height=450, key="map_restaurants")

        # Không có gì → default map
        else:
            default_map = folium.Map(location=[10.776, 106.7], zoom_start=12)
            st_folium(default_map, height=450, key="map_default")

        # ---------------- ROUTE DETAILS ----------------
        if st.session_state.multi_info and not st.session_state.show_default_map:
            st.markdown("---")
            st.markdown("### 🎯 Route Details")

            icons = "🔵🔴🟣🟠🟤"

            for idx, (name, info) in enumerate(st.session_state.multi_info.items(), 1):
                if 'error' in info:
                    st.error(f"❌ {name}: {info['error']}")
                    continue
                    
                with st.expander(
                    f"{icons[(idx - 1) % len(icons)]} {idx}. {name} - {info['distance_km']:.1f} km",
                    icon="📍",
                    expanded=(idx <= 2)
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📏 Distance", f"{info['distance_km']:.2f} km")
                    with col2:
                        st.metric("⏱️ Time", f"{info['duration_hrs']*60:.0f} min")
                    st.caption(f"📍 {info.get('address', 'N/A')}")

#render.py