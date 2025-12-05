from .client import generate_response # Import hàm tạo nội dung
from NLPModule.promptBuilder import buildFixUserSpellingPrompt

def AIFixSpellingErrors(userInput: str):
    # Thay thế client.chat cũ bằng generate_response mới
    prompt = buildFixUserSpellingPrompt(userInput)
    return generate_response(prompt) # generate_response sẽ gọi Gemini 2.5 Flash

# Fix: Bỏ tham số 'self' vì hàm này không nằm trong class (Global Function)
# Hoặc nếu nó là một hàm độc lập (được gọi từ bên ngoài), có thể đổi tên để tránh nhầm lẫn.
def fix(text: str):
    prompt = f"Sửa lỗi chính tả và ngữ pháp cho đoạn văn sau: {text}"
    return generate_response(prompt) # Gọi hàm đã import