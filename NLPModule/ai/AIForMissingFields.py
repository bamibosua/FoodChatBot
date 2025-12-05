# File: AIForMissingFields.py

# 1. Sửa Import: Chỉ import hàm generate_response
from .client import generate_response
from NLPModule.promptBuilder import buildAskMissingPrompt

def aiReplyForMissingFields(missingFields, currentData):
    # 2. Xây dựng prompt
    prompt = buildAskMissingPrompt(missingFields, currentData)
    
    # 3. Thay thế cú pháp client.chat(...) cũ bằng generate_response(prompt)
    # Hàm generate_response sẽ gọi Gemini 2.5 Flash
    return generate_response(prompt)