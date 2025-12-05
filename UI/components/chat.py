# components/chat.py
import streamlit as st
import json
import os
import base64

from UI.config.settings import NUMBER_OF_MESSAGES_TO_DISPLAY
from UI.utils.helpers import save_current_chat, new_chat_id, initialize_conversation

from NLPModule.NLPModule import analyzeUserInput, replyMissingFields, isInHCMMain, reply
from FilterModule.main import app
from Translator.translator import get_original_language, translate_text

def init_food_state():
    defaults = {
        "history": [],
        "conversation_history": initialize_conversation(),
        "final_data": {"location": None, "taste": [], "budget": None, "foods": []},
        "city": None,
        "chat_titles": {},
        "favorites": [],
        "pending_user_input": None,
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

def render_messages():
    for msg in st.session_state.history[-NUMBER_OF_MESSAGES_TO_DISPLAY:]:
        if msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("user", avatar="🙂"):
                st.markdown(msg["content"])

    st.markdown("---")

def process_bot_logic(user_input):
    parsed= analyzeUserInput(user_input)
    st.session_state.original_lang = get_original_language(user_input)
    print(st.session_state.original_lang)
    for key in st.session_state.final_data:
        if parsed.get(key) not in (None, "null", []):
            st.session_state.final_data[key] = parsed[key]

    if parsed.get("city") not in (None, "null", []):
        st.session_state.city = parsed["city"]

    taste_empty = st.session_state.final_data.get("taste") in (None, "null", [])
    foods_empty = st.session_state.final_data.get("foods") in (None, "null", [])

    missing_fields = [
        k
        for k, v in st.session_state.final_data.items()
        if (
            (k in ("taste", "foods") and taste_empty and foods_empty)
            or (k not in ("taste", "foods") and v in (None, "null", [], {}))
        )
    ]

    if not isInHCMMain(st.session_state.city):
        bot_reply = "Currently, the system only supports Ho Chi Minh City.\n"
        bot_reply += "Please enter a location within Ho Chi Minh City."
        if st.session_state.original_lang != 'en':
            bot_reply = translate_text(bot_reply, dest_lang=st.session_state.original_lang)
        return bot_reply
    
    if missing_fields:
        return replyMissingFields(missing_fields, st.session_state.final_data, st.session_state.original_lang)
    
    print(app(st.session_state.final_data))
    print(st.session_state.original_lang)
    bot_reply = reply(app(st.session_state.final_data), st.session_state.original_lang)
    
    st.session_state.final_data = {
        "location": None,
        "taste": [],
        "budget": None,
        "foods": []
    }
    st.session_state.city = None

    return bot_reply


def load_image_base64(relative_path):
    abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Không tìm thấy file: {abs_path}")
    with open(abs_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = load_image_base64("../imgs/logo.png")

def render_main_chat():
    st.markdown(f"""
        <div class="custom-header">
        <h1>
            <img src="data:image/png;base64,{img_base64}" width="100" style="vertical-align: middle; margin-right: 5px;">
            Tourism Chatbot
        </h1>
        <p>Your intelligent travel companion with route planning</p>
        </div>
    """, unsafe_allow_html=True)
        
    init_food_state()

    current_title = st.session_state.chat_titles.get(
        st.session_state.current_chat_id, "New Chat"
    )
    st.markdown(f"**{current_title}**")

    render_messages()

    if st.session_state.pending_user_input:
        user_msg = st.session_state.pending_user_input
        st.session_state.pending_user_input = None

        bot_reply = process_bot_logic(user_msg)

        st.session_state.history.append({"role": "assistant", "content": bot_reply})
        st.session_state.conversation_history.append(
            {"role": "assistant", "content": bot_reply}
        )
        save_current_chat()
        st.rerun()
        
    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})
        st.session_state.conversation_history.append(
            {"role": "user", "content": user_input}
        )
        st.session_state.pending_user_input = user_input
        st.rerun()

    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])

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
                "messages": st.session_state.history,
            }
            st.download_button(
                "Download JSON",
                json.dumps(data, ensure_ascii=False, indent=2),
                f"chat_{st.session_state.current_chat_id}.json",
                "application/json",
            )

    with c4:
        new_name = st.text_input("Rename", placeholder="New name", label_visibility="collapsed")
        if st.button("Rename") and new_name.strip():
            st.session_state.chat_titles[st.session_state.current_chat_id] = new_name.strip()
            st.success("Renamed!")
            st.rerun()