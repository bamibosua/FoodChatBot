import time
import streamlit as st
import pyrebase
import firebase_admin
import requests
from firebase_admin import credentials, firestore
from firebase_admin import auth as admin_auth
from collections import deque
from datetime import datetime, timezone
from ollama import Client
from streamlit_extras.stylable_container import stylable_container
import base64

st.set_page_config(page_title="FOOD CHATBOT")
st.title("Wellcome, _:blue[customer!]:_")

MODEL = "gpt-oss:20b"
client = Client(
    host='http://zvfaa-34-125-183-146.a.free.pinggy.link'
)

# [THAY ĐỔI] — đổi title & icon cho đúng app du lịch
st.set_page_config(
    page_title="Food Chatbot",
    page_icon="🍽️",   # Biểu tượng đĩa thức ăn – chung chung, chuyên nghiệp
    layout="wide"
)

st.markdown(
    """
    <h1 style='color: black; font-family: Times New Roman; font-weight: 700; '>Food Chatbot</h1>
    <p style='font-size: 20px;'>
        <span style='color: black;font-family: Times New Roman;'>
            <i>You want to eat. Log in to chat with our👇<i>
        </span>
    <!-- Divider -->
    <div style='text-align: center; margin: 20px 0;'>
        <hr style='border: 1px solid #7e3412; width: 100%; margin: 0 auto;'>
    </div>
        
    </p>
    """,
    unsafe_allow_html=True
)

# ───────────────────────────────────────────────
# 🔐 LOGIN / SIGNUP (tối giản & UI gọn hơn)
# ───────────────────────────────────────────────
# 🟩 [THAY ĐỔI] — bỏ form chat cũ, chỉ giữ login & signup đơn giản
#take the local picture into background
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def login_form(guest_mode=False):
    with st.empty().container(border=True):
        col1, _, col2 = st.columns([10,1,10])
        
        with col1:
            # Sử dụng ảnh local từ thư mục data
            image_path = "data/background.jpg"
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
                /* Đổi màu chữ input thành đen */
                .stTextInput label {{
                    color: black !important;
                    font-weight: bold;
                }}
                .stTextInput input {{
                    color: black !important;
                }}
            </style>
            '''

            st.markdown(css, unsafe_allow_html=True)
            st.write("")
            st.write("")
            st.markdown("<br>", unsafe_allow_html=True)
            # Hiển thị ảnh với căn chỉnh
            img_base64 = get_base64_image("data/demo1.jpg")
            st.markdown(
                f'''
                <div style="text-align: center;">
                    <img src="data:image/jpeg;base64,{img_base64}" 
                         style="width: 600px; height: 400px; object-fit: cover; border-radius: 20px;">
                </div>
                ''',
            unsafe_allow_html=True)
            #st.image("data/demo1.jpg", use_container_width=True)
        
        with col2:
            st.markdown(
                """
                <h2 style= 
                    'text-align : center; 
                    color: black;
                    font-family: Times New Roman; 
                    margin: 0px'>Login</h2>
                """,
                unsafe_allow_html = True
            )
            
            # Thêm CSS cho text input
            st.markdown(
                """
                <style>
                    div[data-testid="stTextInput"] label {
                        color: black !important;
                        font-weight: 600;
                    }
                    div[data-testid="stTextInput"] input {
                        color: white !important;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            email = st.text_input("E-mail")
            password = st.text_input("Password", type="password")

            # Tạo 3 cột để căn giữa buttons
            col_login, col_signup = st.columns([1, 1])

            with col_login:
                if st.button("Login", type="primary", use_container_width=True):
                    time.sleep(2)
                    if not (email and password):
                        st.error("Please provide email and password")
                    else:
                        st.error("Invalid login credentials")

            with col_signup:
                if st.button("Sign Up", type="primary", use_container_width=True):
                    st.session_state.show_signup = True
                    st.rerun()

def signup_form():
     with st.empty().container(border=True):
        col1, _, col2 = st.columns([10,1,10])
        
        with col1:
            # Sử dụng ảnh local từ thư mục data
            image_path = "data/background.jpg"
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
                /* Đổi màu chữ input thành đen */
                .stTextInput label {{
                    color: black !important;
                    font-weight: bold;
                }}
                .stTextInput input {{
                    color: black !important;
                }}
            </style>
            '''

            st.markdown(css, unsafe_allow_html=True)
            st.write("")
            st.write("")
            st.markdown("<br>", unsafe_allow_html=True)
            # Hiển thị ảnh với căn chỉnh
            img_base64 = get_base64_image("data/demo1.jpg")
            st.markdown(
                f'''
                <div style="text-align: center;">
                    <img src="data:image/jpeg;base64,{img_base64}" 
                         style="width: 500px; height: 300px; object-fit: cover; border-radius: 10px;">
                </div>
                ''',
            unsafe_allow_html=True)
        st.markdown(css, unsafe_allow_html=True)
        with col2:
            st.markdown(
                """
                <h2 style= 
                    'text-align : center; 
                    color: black;
                    font-family: Times New Roman; 
                    margin: 0px'>Sign up</h2>
                """,
                unsafe_allow_html = True
            )
            
            # Thêm CSS cho text input
            st.markdown(
                """
                <style>
                    div[data-testid="stTextInput"] label {
                        color: black !important;
                        font-weight: 600;
                    }
                    div[data-testid="stTextInput"] input {
                        color: white !important;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
            email = st.text_input("Email")
            password = st.text_input("Password (≥6 characters)", type="password")
            col_create, col_back = st.columns(2)
            
            with col_create:
                if st.button("Create Account", type="primary", use_container_width=True):
                    try:
                        auth.create_user_with_email_and_password(email, password)
                        st.success("Sign up successfully. Please login now!")
                        time.sleep(1)  # Cho người dùng thấy thông báo thành công
                        st.session_state.show_signup = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Sign up error: {e}")
            
            with col_back:
                if st.button("Back", type="secondary", use_container_width=True):
                    st.session_state.show_signup = False
                    st.rerun()



def ollama_stream(history_messages: list[dict]):
    """
    Stream tokens from Ollama /api/chat. Yields string chunks suitable for st.write_stream.
    """
    print(history_messages)
    response = client.chat(
        model=MODEL,
        messages=history_messages
    )
    return response['message']['content']

def save_message(uid: str, role: str, content: str):
    doc = {
        "role": role,
        "content": content,
        "ts": datetime.now(timezone.utc)
    }
    db.collection("chats").document(uid).collection("messages").add(doc)

def load_last_messages(uid: str, limit: int = 8):
    q = (db.collection("chats").document(uid)
        .collection("messages")
        .order_by("ts", direction=firestore.Query.DESCENDING)
        .limit(limit))
    docs = list(q.stream())
    docs.reverse()
    out = []
    for d in docs:
        data = d.to_dict()
        out.append({"role": data.get("role", "assistant"),
                    "content": data.get("content", "")})
    return out

params = st.query_params
raw_token = params.get("id_token")
if isinstance(raw_token, list):
    id_token = raw_token[0]
else:
    id_token = raw_token
    
if id_token and not st.session_state.get("user"):
    id_token = params["id_token"][0]
    try:
        decoded = admin_auth.verify_id_token(id_token)
        st.session_state.user = {
            "email": decoded.get("email"),
            "uid": decoded.get("uid"),
            "idToken": id_token,
        }
        msgs = []
        try:
            msgs = load_last_messages(st.session_state.user["uid"], limit=8)
        except Exception:
            pass
        st.session_state.messages = deque(
            msgs if msgs else [{"role": "assistant", "content": "Xin chào Xin chào 👋! Tôi là Mika. Tôi có thể giúp gì cho bạn?"}],
            maxlen=8
        )
        st.experimental_set_query_params()
        st.success("Đăng nhập Google thành công!")
        st.rerun()
    except Exception as e:
        st.error(f"Xác thực Google thất bại: {e}")


@st.cache_resource
def get_firebase_clients():
    # Pyrebase (Auth)
    firebase_cfg = st.secrets["firebase_client"]
    firebase_app = pyrebase.initialize_app(firebase_cfg)
    auth = firebase_app.auth()

    # Admin (Firestore)
    if not firebase_admin._apps:
        cred = credentials.Certificate(dict(st.secrets["firebase_admin"]))
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    return auth, db

auth, db = get_firebase_clients()


if "user" not in st.session_state:
    st.session_state.user = None 

if "messages" not in st.session_state:
    st.session_state.messages = deque([
        {"role": "assistant", "content": "Xin chào Xin chào 👋! Tôi là Mika. Tôi có thể giúp gì cho bạn?"}
    ], maxlen=8)
else:
    if not isinstance(st.session_state.messages, deque):
        st.session_state.messages = deque(st.session_state.messages[-8:], maxlen=8)

if "chat_open" not in st.session_state:
    st.session_state.chat_open = False

def login_form():
    st.markdown("<h3 style='text-align: center;'>Đăng nhập</h3>", unsafe_allow_html=True)
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", key="email_login")
        password = st.text_input("Mật khẩu", type="password", key="password_login")
        col1, _, col2 = st.columns([0.75, 0.75, 0.75])
        with col1:
            with stylable_container(
                "black",
                css_styles="""
                button {
                    background-color: #0DDEAA;
                    color: black;
                }""",
            ):
                login = st.form_submit_button("Đăng nhập")
        with col2:
            goto_signup = st.form_submit_button("Chưa có tài khoản? Đăng ký", type="primary")

    if goto_signup:
        st.session_state["show_signup"] = True
        st.session_state["show_login"] = False
        st.rerun()

    if login:
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            # user: dict có idToken, refreshToken, localId (uid), email
            st.session_state.user = {
                "email": email,
                "uid": user["localId"],
                "idToken": user["idToken"]
            }
            # tải lịch sử gần nhất từ Firestore
            msgs = load_last_messages(st.session_state.user["uid"], limit=8)
            if msgs:
                st.session_state.messages = deque(msgs, maxlen=8)
            else:
                st.session_state.messages = deque([
                    {"role": "assistant", "content": "Xin chào Xin chào 👋! Tôi là Mika. Tôi có thể giúp gì cho bạn?"}
                ], maxlen=8)
            st.success("Đăng nhập thành công!")
            st.rerun()
        except Exception as e:
            st.error(f"Đăng nhập thất bại: {e}")

def signup_form():
    st.subheader("Đăng ký")
    with st.form("signup_form", clear_on_submit=False):
        email = st.text_input("Email", key="email_signup")
        password = st.text_input("Mật khẩu (≥6 ký tự)", type="password", key="password_signup")
        col1, _, col2 = st.columns([0.75, 0.75, 0.75])
        with col1:
            with stylable_container(
                "black-1",
                css_styles="""
                button {
                    background-color: #0DD0DE;
                    color: black;
                }""",
            ):
                signup = st.form_submit_button("Tạo tài khoản")
        with col2:
                goto_login = st.form_submit_button("Đã có tài khoản? Đăng nhập", type="primary")

    if goto_login:
        st.session_state["show_signup"] = False
        st.session_state["show_login"] = True
        st.rerun()

    if signup:
        try:
            user = auth.create_user_with_email_and_password(email, password)
            st.success("Tạo tài khoản thành công! Vui lòng đăng nhập.")
            time.sleep(3)
            st.session_state["show_signup"] = False
            st.session_state["show_login"] = True
            st.rerun()
        except Exception as e:
            st.error(f"Đăng ký thất bại: {e}")

@st.dialog("Trợ lý Mika")
def chat_dialog():
    if not st.session_state.user:
        st.info("Bạn cần đăng nhập để chat và lưu lịch sử.")
        return
    
    chat_body = st.container(height=600, border=True)

    def render_history():
        chat_body.empty()
        with chat_body:
            for msg in list(st.session_state.messages):
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
    render_history()

    user_input = st.chat_input("Nhập tin nhắn...", key="dialog_input")
        
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_body:
            with st.chat_message("user"):
                st.markdown(user_input)
        save_message(st.session_state.user["uid"], "user", user_input)
        try:
            reply = ollama_stream(st.session_state.messages)
        except requests.RequestException as e:
            st.error(f"Ollama request failed: {e}")
            reply = ""
        st.session_state.messages.append({"role": "assistant", "content": reply})
        save_message(st.session_state.user["uid"], "assistant", reply)
        st.session_state.chat_open = True
        st.rerun()

st.markdown("<h1 style='text-align: center;'>Streamlit Chat + Firebase Login</h1>", unsafe_allow_html=True)

if "show_signup" not in st.session_state:
    st.session_state["show_signup"] = False
if "show_login" not in st.session_state:
    st.session_state["show_login"] = True

if st.session_state.user:
    st.success(f"Đang đăng nhập: {st.session_state.user['email']}")
    _, col2, _ = st.columns([1.3, 0.75, 1])
    with col2:
        if st.button("Đăng xuất", type="primary"):
            st.session_state.user = None
            st.session_state.chat_open = False
            st.rerun()
else:
    if st.session_state.get("show_signup", False):
        signup_form()
    elif st.session_state.get("show_login", True):
        login_form()

st.divider()
st.markdown("<h5 style='text-align: center;'>Click 💬 để mở hộp thoại chat</h5>", unsafe_allow_html=True)

st.markdown('<div id="fab-anchor"></div>', unsafe_allow_html=True)
with stylable_container(
                "black-3",
                css_styles="""
                button {
                    background-color: #66c334;
                    color: black;
                    width: 704px !important; 
                    height: 30px; 
                }""",
            ):
    fab_clicked = st.button("💬", key="open_chat_fab", help="Mở chat")
    
if fab_clicked:
    st.session_state.chat_open = True
    st.rerun()

if st.session_state.chat_open:
    chat_dialog()


st.markdown("""
<style>
#fab-anchor + div button {
    position: fixed;
    bottom: 16px;
    right: 16px;
    width: 120px !important; 
    height: 60px; 
    border-radius: 50%;
    font-size: 26px; 
    line-height: 1; 
    padding: 0;
    box-shadow: 0 6px 18px rgba(0,0,0,0.25);
    z-index: 10000;
}
#fab-anchor + div button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 24px rgba(250,206,175,0.28);
}
</style>
""", unsafe_allow_html=True)
