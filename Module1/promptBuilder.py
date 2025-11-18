def buildExtractPrompt(input: str):
    return f"""

"Hãy phân tích câu sau và trả lời DUY NHẤT bằng JSON hợp lệ."
"Không được thêm giải thích, text thừa, markdown hay code block."
"Schema JSON:"
"
'  "location_ai": string hoặc null,'
'  "tasteAndFood_ai": [string], [string],...'
'  "budget_raw": string hoặc null'
"

Yêu cầu:
- location_ai: địa điểm nếu người dùng nói rõ (quận, huyện, khu vực). Nếu không có thì ghi "null".
Không bao giờ được trả về nội dung viết tắt.
- tasteAndFood_ai: danh sách khẩu vị nếu có thể nhận biết. Hoặc có thể là một món ăn cụ thể.
Nếu không có thì trả mảng rỗng [].
- budget_raw: trích số tiền EXACT như người dùng nhập (có thể 100k, 1tr2, 50-100k...). 
Không cần chuẩn hóa. Nếu không có thì ghi "null".

Không giải thích thêm.

Câu người dùng: "{input}"
"""

def buildAskMissingPrompt(missing_fields, current_data):
    return f"""
    Bạn là trợ lý hội thoại. Dựa trên các trường còn thiếu trong dữ liệu của người dùng, 
    hãy tạo câu hỏi tự nhiên, thân thiện để yêu cầu bổ sung.

    Dữ liệu hiện tại: {current_data}
    Trường còn thiếu: {missing_fields}

    - Viết câu hỏi ngắn gọn, rõ ràng.
    - Không liệt kê field thô, hãy chuyển thành câu hỏi tự nhiên.
    Trả về câu hỏi dạng plain text.
    """