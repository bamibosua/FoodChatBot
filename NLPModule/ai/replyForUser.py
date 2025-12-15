# NLPModule/ai/replyForUser.py
from .client import generate_response
from .promptBuilder import buildReplyForUserPrompt

def replyForUser(data: dict, userLanguage):
    prompt = buildReplyForUserPrompt(data, userLanguage)
    
    # System instruction trung lập, để AI tự quyết định theo Prompt
    system_instr = "You are a smart, multi-lingual food assistant. Adapt strictly to the user's language and context."
    
    # Dùng model Smart (17b hoặc 70b) để logic ngôn ngữ tốt nhất
    return generate_response(prompt, system_instruction=system_instr)