import streamlit as st

def apply_main_styles():
        """Apply main CSS styles."""
        st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <style>
            /* Main background */
            [data-testid="stAppViewContainer"] {
                #background: linear-gradient(135deg, #fff176 0%, #6a1b9a 100%);
                height: 100vh;
            }
            
            /* Sidebar styling */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
                color: #ecf0f1;
                padding: 20px;
                border-top-right-radius: 20px;
                border-bottom-right-radius: 20px;
                box-shadow: 2px 0 10px rgba(0, 0, 0, 0.2);
            }
            
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
                color: #ecf0f1 !important;
            }
            
            /* Sidebar buttons */
            [data-testid="stSidebar"] button {
                background-color: rgba(255, 255, 255, 0.1) !important;
                color: white !important;
                border-radius: 10px !important;
                margin: 5px 0;
                padding: 8px 12px;
                border: none !important;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            [data-testid="stSidebar"] button:hover {
                background-color: rgba(255, 255, 255, 0.2) !important;
                transform: translateX(2px);
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
                background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
                color: purple;
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
            
            /* Text input styling */
            div[data-testid="stTextInput"] label {
                color: black !important;
                font-weight: 600;
            }
            
            div[data-testid="stTextInput"] input {
                color: black !important;
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
                color: purple;
                text-align: center;
                margin: 10px 0;
                font-weight: bold;
            }
        </style>
        """, unsafe_allow_html=True)

def apply_sidebar_styles():
        st.markdown("""
            <style>
                [data-testid="stAppViewContainer"],
                .stApp {
                    background: linear-gradient(135deg, #fff176 0%, #6a1b9a 100%) !important;
                    background-attachment: fixed;
                }
                /* Tùy chọn: làm sidebar trong suốt hơn */
                [data-testid="stSidebar"] {
                    background: rgba(30, 60, 114, 0.95) !important;
                    backdrop-filter: blur(10px);
                }
            </style>
            """, unsafe_allow_html=True)