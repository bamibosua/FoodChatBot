# components/sidebar.py
import streamlit as st
from UI.utils.helpers import save_current_chat, new_chat_id, initialize_conversation, get_chat_preview

def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div class="user-badge">
            User: {st.session_state.username}
        </div>
        """, unsafe_allow_html=True)

        if st.button("Log out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

        st.markdown("---")

        if st.checkbox("🗺 Show Map", value=st.session_state.show_map_sidebar):
            st.session_state.show_map_sidebar = True
        else:
            st.session_state.show_map_sidebar = False

        menu = st.radio(
            "Select Function:",
            ["New Chat!", "History", "Favorites", "Settings"],
            index=0
        )

        st.markdown("Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Chats", len(st.session_state.all_chats))
        with col2:
            st.metric("Favorites", len(st.session_state.favorites))
        st.markdown("---")
        
        if menu == "New Chat!":
            st.markdown("Start New Chat!")
            if st.button("Create New Chat!", use_container_width=True):
                if st.session_state.current_chat_id:
                    save_current_chat()
                cid = new_chat_id()
                st.session_state.current_chat_id = cid
                st.session_state.history = []
                st.session_state.conversation_history = initialize_conversation()
                st.rerun()

        elif menu == "History":
            st.markdown("Conversation History")
            if st.session_state.all_chats:
                search = st.text_input("Search", "")
                ordered = sorted(st.session_state.all_chats.items(),
                               key=lambda x: x[1].get("timestamp", ""), reverse=True)
                for chat_id, data in ordered:
                    preview = get_chat_preview(data.get("history", []))
                    title = data.get("title", chat_id)[:30]
                    if search.lower() not in preview.lower() and search.lower() not in title.lower():
                        continue
                    with st.expander(f"{title}..."):
                        st.write(f"Time: {data.get('timestamp', '')}")
                        st.write(f"Preview: {preview}")
                        c1, c2 = st.columns(2)
                        if c1.button("Load", key=f"load_{chat_id}"):
                            save_current_chat()
                            st.session_state.current_chat_id = chat_id
                            st.session_state.history = data["history"].copy()
                            st.session_state.conversation_history = initialize_conversation()
                            st.rerun()
                        if c2.button("Delete", key=f"del_{chat_id}"):
                            st.session_state.all_chats.pop(chat_id, None)
                            if st.session_state.current_chat_id == chat_id:
                                st.session_state.current_chat_id = None
                            st.rerun()
            else:
                st.info("No chat history yet.")

        elif menu == "Favorites":
            st.markdown("Favorites")
            if st.session_state.favorites:
                for i, fav in enumerate(st.session_state.favorites, 1):
                    with st.expander(f"Favorite {i}"):
                        st.write(fav[:100] + "..." if len(fav) > 100 else fav)
                        if st.button("Remove", key=f"rem_fav_{i}"):
                            st.session_state.favorites.remove(fav)
                            st.rerun()
                if st.button("Clear All", use_container_width=True):
                    st.session_state.favorites = []
                    st.rerun()
            else:
                st.info("No favorites yet.")

        elif menu == "Settings":
            st.markdown("Settings")
            st.selectbox("Theme", ["Light Yellow", "Blue", "Green", "Orange", "Pink", "Purple"])
            st.slider("Messages to show", 10, 100, 50)
            if st.button("Save Settings"):
                st.success("Saved!")

    return menu