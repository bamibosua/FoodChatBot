# components/sidebar.py
import streamlit as st
import os
import json
from datetime import datetime

from UI.utils.helpers import apply_header_sidebar_styles, get_chat_title, load_user_chats
from UI.utils.helpers import save_chat_history_to_file, initialize_conversation
from UI.utils.helpers import load_chat_history_from_file, save_current_chat, new_chat_id, get_chat_preview

def render_sidebar():
    with st.sidebar:
        # Header với user info
        apply_header_sidebar_styles()
        # Action buttons
        if st.button("Log out", use_container_width=True, help="Logout"):
            save_current_chat()
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

        # Map toggle
        if st.checkbox("🗺 Show Map", value=st.session_state.get('show_map_sidebar', False)):
            st.session_state.show_map_sidebar = True
        else:
            st.session_state.show_map_sidebar = False

        # Metrics
        st.metric("Chats", len(st.session_state.get('all_chats', {})))

        # NEW CHAT SECTION
        st.markdown("### 💬 New Chat")
        if st.button("Create New Chat", use_container_width=True, type="primary"):
            save_current_chat()  # Lưu chat hiện tại trước khi tạo mới
            cid = new_chat_id()
            st.session_state.current_chat_id = cid
            st.session_state.history = []
            st.session_state.conversation_history = initialize_conversation(st.session_state.current_chat_id, st.session_state.username)
            
            # RESET MAP VỀ MẶC ĐỊNH KHI TẠO CHAT MỚI
            reset_map_to_default()
            
            st.toast("New chat created!")
            st.rerun()

        st.markdown("---")

        # CHAT HISTORY SECTION
        with st.expander("Chat History", expanded=True):
            if st.session_state.get('all_chats'): # kiem tra all chats co ton tai, neu co thi hien thi, neu khong thi hien thi thong bao
                # Search
                search = st.text_input("Search", placeholder="Search chats...", label_visibility="collapsed")
                
                # Sort theo timestamp
                ordered = sorted(
                    st.session_state.all_chats.items(),
                    key=lambda x: x[1].get("timestamp", ""), 
                    reverse=True # latest first
                )
                
                st.caption(f"Total: {len(ordered)} chats") # hien thi tong so chat
                
                # Display chats
                for chat_id, data in ordered[:10]:  # Show only latest 10
                    preview = get_chat_preview(data.get("history", []))
                    title = data.get("title", chat_id)
                    
                    if search.lower() and search.lower() not in preview.lower() and search.lower() not in title.lower():
                        continue
                    
                    is_current = (chat_id == st.session_state.get('current_chat_id'))
                    
                    # Chat item card với màu sắc được cải thiện (them vao styles.py)
                    bg_color = "#e3f2fd" if is_current else "#f5f5f5"
                    border_color = "#1976d2" if is_current else "#bdbdbd"
                    text_color = "#1565c0" if is_current else "#424242"
                    
                    # hien thi ten doan chat theo user input va thoi gian
                    st.markdown(f"""
                    <div style="background-color: {bg_color}; padding: 10px; 
                                border-radius: 8px; margin-bottom: 8px; border-left: 3px solid {border_color};
                                transition: all 0.2s ease;">
                        <b style="color: {text_color};">{'▶️ ' if is_current else ''}{title[:40]}</b><br>
                        <small style="color: #757575;">{data.get('timestamp', '')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action buttons for each chat
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        # save current chat, load new chat, rerun
                        if st.button("Load", key=f"load_{chat_id}", use_container_width=True):
                            save_current_chat()
                            st.session_state.current_chat_id = chat_id
                            st.session_state.history = data["history"].copy()
                            st.session_state.conversation_history = initialize_conversation(st.session_state.current_chat_id, st.session_state.username)
                            st.rerun()
                    with c2:
                        # Tạo key confirm riêng cho mỗi chat
                        confirm_key = f"confirm_del_{chat_id}"

                        # Nếu người dùng chưa xác nhận
                        if not st.session_state.get(confirm_key, False):
                            if st.button("Remove", key=f"del_{chat_id}", use_container_width=True):
                                # Kích hoạt trạng thái xác nhận
                                st.session_state[confirm_key] = True
                                st.rerun()
                        else:
                            # Hộp xác nhận xóa
                            st.warning("Confirm delete?", icon="⚠️")

                            col_yes, col_no = st.columns([1, 1])

                            with col_yes:
                                if st.button("Yes", key=f"yes_{chat_id}", use_container_width=True):
                                    st.session_state.all_chats.pop(chat_id, None)
                                    if st.session_state.get('current_chat_id') == chat_id:
                                        st.session_state.current_chat_id = None

                                    save_chat_history_to_file(st.session_state.username, st.session_state.all_chats)

                                    # Reset trạng thái confirm
                                    st.session_state.pop(confirm_key, None)

                                    if(st.session_state.get('current_chat_id') is None):
                                        # Tạo chat mới hoàn toàn
                                        cid = new_chat_id()
                                        st.session_state.current_chat_id = cid
                                        st.session_state.history = []  # Clear history cũ
                                        st.session_state.conversation_history = []  # Clear conversation cũ
                                        
                                        # RESET MAP VỀ MẶC ĐỊNH KHI TẠO CHAT MỚI
                                        reset_map_to_default()

                                    st.rerun()

                            with col_no:
                                if st.button("No", key=f"no_{chat_id}", use_container_width=True):
                                    # Hủy xác nhận
                                    st.session_state.pop(confirm_key, None)
                                    st.rerun()

                if len(ordered) > 10:
                    st.caption(f"... and {len(ordered) - 10} more chats")

                # Management buttons
                if st.button("Clear All History", type="primary", use_container_width=True):
                    # Clear toàn bộ chats
                    st.session_state.all_chats = {}
                    save_chat_history_to_file(st.session_state.username, {})
                    
                    # Tạo chat mới hoàn toàn
                    cid = new_chat_id()
                    st.session_state.current_chat_id = cid
                    st.session_state.history = []  # Clear history cũ
                    st.session_state.conversation_history = []  # Clear conversation cũ
                    
                    # RESET MAP VỀ MẶC ĐỊNH KHI XÓA TẤT CẢ
                    reset_map_to_default()
                    
                    st.toast("All chats cleared! New chat created.")
                    st.rerun()
            else:
                st.info("No chats yet. Start chatting!")

def reset_map_to_default():
    """Reset toàn bộ dữ liệu map về trạng thái mặc định"""
    map_defaults = {
        "current_location": "",
        "current_location_input": "",
        "last_valid_location": None,
        "multi_map": None,
        "multi_info": {},
        "show_default_map": True,
        "map_key": "map_default",
        "route_error": None,
        "filtered_restaurants": [],
        "previous_restaurants_ids": None,
    }
    
    for key, value in map_defaults.items():
        st.session_state[key] = value