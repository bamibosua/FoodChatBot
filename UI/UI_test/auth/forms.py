import streamlit as st
import base64
from utils.helpers import get_base64_image
from config.settings import auth

def login_form(guest_mode=False):
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
    with st.empty().container(border=False):
        col1, _, col2 = st.columns([1,0.05,1])
        
        with col1:
            # Sử dụng ảnh local từ thư mục data
            image_path = "imgs/background.png"
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
            img_base64 = get_base64_image("imgs/demo1.jpg")
            st.markdown(
                f'''
                <div style="text-align: center;">
                    <img src="data:image/jpeg;base64,{img_base64}" 
                         style="width: 500px; height: 300px; object-fit: cover; border-radius: 20px;">
                         <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
                            <img style="width: 100%; height: auto; max-height: 400px; ...">
                         </div>
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
                        color: black !important;
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
                if st.button("Login", use_container_width=True):
                    try:
                         user = auth.sign_in_with_email_and_password(email, password)
                         st.session_state.logged_in = True
                         st.session_state.username = email.split('@')[0]
                         st.success("Login successful!")
                         st.rerun()
                    except Exception as e:
                            error_message = str(e)
                            if "INVALID_PASSWORD" in error_message or "INVALID_LOGIN_CREDENTIALS" in error_message:
                                st.error("Invalid email or password")
                            elif "EMAIL_NOT_FOUND" in error_message:
                                st.error("Email not found. Please sign up first.")
                            elif "TOO_MANY_ATTEMPTS" in error_message:
                                st.error("Too many failed attempts. Please try again later.")
                            else:
                                st.error("Invalid email or password")
            with col_signup:
                if st.button("Sign Up", use_container_width=True):
                    st.session_state.show_signup = True
                    st.rerun()

def signup_form():
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
    unsafe_allow_html=True)
    
     with st.empty().container(border=False):
        col1, _, col2 = st.columns([10,1,10])
        
        with col1:
            # Sử dụng ảnh local từ thư mục data
            image_path = "imgs/background.png"
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
            img_base64 = get_base64_image("imgs/demo1.jpg")
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
                        color: black !important;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
            email = st.text_input("Email")
            password = st.text_input("Password (≥6 characters)", type="password")
            col_create, col_back = st.columns(2)
            
            if st.button("Create Account", type="primary", use_container_width=True):
                    try:
                        user = auth.create_user_with_email_and_password(email, password)
                        st.success("Sign up successfully. Please login now!")
                         # Cho người dùng thấy thông báo thành công
                        st.session_state.show_signup = False
                        st.rerun()
                    except Exception as e:
                        error_message = str(e)
                        if "INVALID_PASSWORD" in error_message or "INVALID_LOGIN_CREDENTIALS" in error_message:
                                st.error("Invalid email or password")
                        elif "EMAIL_NOT_FOUND" in error_message:
                                st.error("Email not found. Please sign up first.")
                        elif "TOO_MANY_ATTEMPTS" in error_message:
                                st.error("Too many failed attempts. Please try again later.")
                        elif "WEAK_PASSWORD" in error_message:
                                st.error("Weak password. Please use at least 6 characters.")    
                        elif "EMAIL_EXISTS" in error_message:
                                st.error("Email already exists. Please use a different email.")
                        else:
                                st.error(f"Login error: {error_message}")
            
            with col_back:
                if st.button("Back", type="secondary", use_container_width=True):
                    st.session_state.show_signup = False
                    st.rerun()
