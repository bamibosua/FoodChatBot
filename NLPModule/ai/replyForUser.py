# File: NLPModule/ai/replyForUser.py

# Sửa Import: 
from .client import generate_response 
# Import hàm xây dựng prompt mới của bạn
from NLPModule.promptBuilder import buildReplyForUserPrompt 

def replyForUser(inputData: dict):
    """
    Tạo phản hồi cho người dùng dựa trên dữ liệu nhà hàng (mainRes, supportRes) 
    và sử dụng prompt định dạng sáng tạo.
    """
    
    # 1. Xây dựng prompt
    # inputData chứa dữ liệu nhà hàng mà bạn muốn hiển thị
    prompt = buildReplyForUserPrompt(inputData)
    
    # 2. Thay thế logic Ollama cũ bằng generate_response (Gemini)
    # Hàm generate_response sẽ gọi Gemini 2.5 Flash và trả về chuỗi đã được định dạng
    response_text = generate_response(prompt)
    
    return response_text