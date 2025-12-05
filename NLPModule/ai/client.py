import google.generativeai as genai
import os

# KHÔNG KHAI BÁO biến client hay MODEL ở cấp độ cao nhất
MODEL_NAME = "gemini-2.5-flash"  # Tên model bạn muốn dùng

# Lấy key từ biến môi trường hoặc dùng key cứng (tạm thời)
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD3b52kkvCkB3wW78NzXOWCIspO_Mk6joI") 
genai.configure(api_key=API_KEY)

# Hàm được thiết kế để các file khác sử dụng
def generate_response(prompt: str):
    """Sử dụng Gemini để tạo nội dung từ prompt."""
    model_instance = genai.GenerativeModel(MODEL_NAME)
    response = model_instance.generate_content(prompt)
    return response.text