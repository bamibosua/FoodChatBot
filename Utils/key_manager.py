# key_manager.py

# Tổng hợp tất cả key free vào đây
SHARED_GEMINI_KEYS = [
    "AIzaSyCQnxAYMlfsh7PK93u8vk3GGQGjp247UA4",    # Key 8
]

SHARED_GROQ_KEYS = ["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"]

SERP_API_KEY_CONSTANT = "ed7e0f948642507971435618a25e646ddb5d2e9f5d46f7b84db783108e232800"

GEMINI_MODEL_NAME_CONSTANT = "gemini-2.5-flash"
GROQ_MODEL_SMART = "llama-3.3-70b-versatile" # 70B (1K RPD)
GROQ_MODEL_FAST = "llama-3.1-8b-instant"     # 8B (14.4K RPD)

def get_gemini_keys():
    return SHARED_GEMINI_KEYS

def get_groq_keys():
    return SHARED_GROQ_KEYS

def get_serp_key():
    return SERP_API_KEY_CONSTANT

# Thêm hàm lấy tên model
def get_groq_smart_model():
    return GROQ_MODEL_SMART

def get_groq_fast_model():
    return GROQ_MODEL_FAST

def get_gemini_model():
    return GEMINI_MODEL_NAME_CONSTANT