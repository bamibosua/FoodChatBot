# NLPModule/ai/client.py (ĐÃ CHUYỂN HOÀN TOÀN SANG GROQ)
from groq import Groq
import google.generativeai as genai
from Utils.key_manager import get_gemini_keys, get_groq_keys, get_groq_smart_model, get_groq_fast_model, get_gemini_model

def generate_response(prompt: str, system_instruction: str = "You are a helpful assistant.", model_type="smart"):
    """
    Hàm gọi AI sử dụng Groq với cơ chế xoay vòng Key và chọn model linh hoạt.
    model_type: "smart" (70b - mặc định) hoặc "fast" (8b)
    """
    keys = get_groq_keys()
    
    # Chọn model dựa trên tham số truyền vào
    if model_type == "fast":
        model_name = get_groq_fast_model()
    else:
        model_name = get_groq_smart_model()
    
    for i, key in enumerate(keys):
        try:
            client = Groq(api_key=key)
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                model=model_name,
                temperature=0.6,
                max_tokens=4096,
                top_p=1,
                stream=False,
            )
            return chat_completion.choices[0].message.content

        except Exception as e:
            # print(f"⚠️ [Groq-{model_name}] Key #{i+1} lỗi: {e}") 
            continue 

    return "Hệ thống đang bận, vui lòng thử lại sau giây lát."

def gemini_generate_response(prompt: str):
    """
    Hàm gọi AI 'Bất tử': Tự động đổi key nếu key hiện tại hết quota.
    """
    keys = get_gemini_keys() # Lấy danh sách key
    
    for i, key in enumerate(keys):
        try:
            # 1. Cấu hình lại với key mới trong vòng lặp
            genai.configure(api_key=key)
            
            # 2. Khởi tạo model
            model_instance = genai.GenerativeModel(get_gemini_model())
            
            # 3. Gọi API
            # Thêm generation_config để đảm bảo trả về text ổn định, không bị block
            response = model_instance.generate_content(
                prompt,
                generation_config={"temperature": 0.7} 
            )
            
            # 4. Thành công -> Trả về text ngay
            return response.text

        except Exception as e:
            # 5. Nếu lỗi -> In ra console để biết và thử key tiếp theo
            print(f"⚠️ [Client AI] Key #{i+1} lỗi: {e}")
            print(f"🔄 Đang chuyển sang Key dự phòng...")
            continue 

    # Nếu thử hết key mà vẫn lỗi
    return "Xin lỗi, hệ thống AI đang quá tải. Vui lòng thử lại sau giây lát."