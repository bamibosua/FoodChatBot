# components/chat.py
import streamlit as st
import json
from openai import OpenAI
from config.settings import client, DEFAULT_MODEL, NUMBER_OF_MESSAGES_TO_DISPLAY
from utils.helpers import save_current_chat, new_chat_id, initialize_conversation

def render_main_chat(menu):
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