# components/chat.py
import streamlit as st
import base64
import os
import json
from openai import OpenAI
from config.settings import client, DEFAULT_MODEL, NUMBER_OF_MESSAGES_TO_DISPLAY
from utils.helpers import save_current_chat, new_chat_id, initialize_conversation

def load_image_base64(relative_path):
    # Lấy đường dẫn tuyệt đối từ vị trí file này
    abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Không tìm thấy file: {abs_path}")
    with open(abs_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Sử dụng
img_base64 = load_image_base64("../imgs/logo.png")  # từ components/chat.py

def render_main_chat(menu):
    
    st.markdown(f"""
<div class="custom-header">
    <h1>
        <img src="data:image/png;base64,{img_base64}" width="100" style="vertical-align: middle; margin-right: 5px;">
        Tourism Chatbot
    </h1>
    <p>Your intelligent travel companion with route planning</p>
</div>
""", unsafe_allow_html=True)

    # Ensure current chat exists
    if not st.session_state.current_chat_id:
        cid = new_chat_id()
        st.session_state.current_chat_id = cid
        st.session_state.history = []
        st.session_state.conversation_history = initialize_conversation()

    current_title = st.session_state.chat_titles.get(st.session_state.current_chat_id, "New Chat")
    st.markdown(f"**{current_title}**")

    # Display messages
    for idx, msg in enumerate(st.session_state.history[-NUMBER_OF_MESSAGES_TO_DISPLAY:]):
        if msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="Robot"):
                st.write(msg["content"])
                if st.button("Heart", key=f"fav_{idx}"):
                    if msg["content"] not in st.session_state.favorites:
                        st.session_state.favorites.append(msg["content"])
                        st.success("Saved to favorites!")
        else:
            with st.chat_message("user"):
                st.write(msg["content"])

    st.markdown("---")
    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})
        st.session_state.conversation_history.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            try:
                resp = client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=st.session_state.conversation_history
                )
                reply = resp.choices[0].message.content
            except Exception as e:
                reply = f"Error: {e}"

        st.session_state.history.append({"role": "assistant", "content": reply})
        st.session_state.conversation_history.append({"role": "assistant", "content": reply})
        save_current_chat()
        st.rerun()

    # Bottom controls
    c1, c2, c3, c4 = st.columns([1,1,1,2])
    with c1:
        if st.button("Save"):
            save_current_chat()
            st.success("Saved!")
    with c2:
        if st.button("Clear"):
            st.session_state.history = []
            st.rerun()
    with c3:
        if st.button("Export"):
            data = {
                "chat_id": st.session_state.current_chat_id,
                "title": current_title,
                "messages": st.session_state.history
            }
            st.download_button("Download JSON", json.dumps(data, ensure_ascii=False, indent=2),
                             f"chat_{st.session_state.current_chat_id}.json", "application/json")
    with c4:
        new_name = st.text_input("Rename", placeholder="New name", label_visibility="collapsed")
        if st.button("Rename"):
            if new_name.strip():
                st.session_state.chat_titles[st.session_state.current_chat_id] = new_name.strip()
                st.success("Renamed!")
                st.rerun()