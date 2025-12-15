import streamlit as st
import base64
from UI.utils.helpers import get_base64_image
from UI.config.settings import auth
from UI.utils.helpers import title_form, background_image, food_image
from UI.auth.logics import handle_login, handle_signup
from UI.config.styles import get_login_title_style, get_signup_title_style, get_forgot_password_title_style, get_image_container_style

#========================================FORMS =======================================
def login_form(guest_mode=False):
    #Header và mô tả
    title_form()

    with st.empty().container(border=False):
        col1, _, col2 = st.columns([1,0.05,1])

        # background image
        background_image()
        
        # Cột bên trái với hình ảnh VietNam food
        with col1:
            #css dung dieu chinh chieu cao cua khung hinh anh
            st.markdown(get_image_container_style(height="20px"), unsafe_allow_html=True)
            food_image()
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown(get_login_title_style(), unsafe_allow_html=True)

            with st.form("login_form"):
                email = st.text_input("E-mail", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="Your password")

                #Tạo 3 cột để căn giữa buttons
                col_login, col_signup, col_forgot = st.columns([1, 1, 1])

                with col_login:
                    # Button Login
                    if st.form_submit_button("Login", use_container_width=True):
                        handle_login(email, password)
                # Buttons Sign Up
                with col_signup:
                    if st.form_submit_button("Sign Up", use_container_width=True):
                        st.session_state.show_signup = True # Chuyển sang form đăng ký
                        st.rerun()
                # Button Forgot Password
                with col_forgot:
                    if st.form_submit_button("Forgot Password?", use_container_width=True):
                        st.session_state.show_forgot = True
                        st.rerun()

def signup_form():
     
    title_form()

    with st.empty().container(border=False):
        col1, _, col2 = st.columns([10,1,10])
        #Sử dụng ảnh local từ thư mục data
        background_image()
        with col1:    
            #Css dùng để điều chỉnh chiều cao của khung hình ảnh
            st.markdown(get_image_container_style(height="20px"), unsafe_allow_html=True)
            food_image()
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(get_signup_title_style(), unsafe_allow_html=True)
            with st.form("signup_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password (≥6 characters)", placeholder="At least 6 characters", type="password")

                col_create, col_back = st.columns([1, 1])

                with col_create:
                    
                    if st.form_submit_button("Create Account", type="secondary", use_container_width=True):
                        handle_signup(email, password)
                with col_back:
                    if st.form_submit_button("Back", type="secondary", use_container_width=True):
                        st.session_state.show_signup = False
                        st.rerun()

def forgot_password_form():

    title_form()
    background_image()
    col1, _, col2 = st.columns([1,0.05,1])
    with col1:
        food_image()
    with col2:
        st.markdown(get_forgot_password_title_style(), unsafe_allow_html=True)

        with st.form("forgot_password_form"):
            email = st.text_input("Registered Email", placeholder="you@example.com")
            col1, col2 = st.columns([1, 1])
            with col1:
                submit_button = st.form_submit_button("Send Reset Link", use_container_width=True)
            with col2:
                if st.form_submit_button("Back", use_container_width=True):
                    st.session_state.show_forgot = False
                    st.rerun()
                

        if submit_button:
            if email:
                try:
                    user = auth.send_password_reset_email(email) # dùng thư viện firebase để gửi email reset password (pyrebase)
                    st.success("Reset link sent successfully!")
                    st.info("Check your inbox (and Spam folder)!")
                    st.balloons()
                    st.session_state.show_forgot = False
                    st.rerun()
                except Exception as e:
                    st.error("Email does not exist or system error!")
                else:
                    st.error("Please enter your email!")

def verify_email_form():
    st.markdown(
        """
        <h2 style= 
            'text-align : center; 
            color: black;
            font-family: Times New Roman; 
            margin: 0px'>Verify Email</h2>
        """,
        unsafe_allow_html = True
    )
    st.info("A verification link has been sent to your email. Please check your inbox and click the link to verify your account.")
    if st.button("Back to Login", use_container_width=True):
        st.session_state.show_verify = False
        st.rerun()