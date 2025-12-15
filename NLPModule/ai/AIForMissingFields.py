# NLPModule/ai/AIForMissingFields.py
from .client import generate_response
from .promptBuilder import buildAskMissingPrompt

def aiReplyForMissingFields(missingFields, currentData):
    prompt = buildAskMissingPrompt(missingFields, currentData)
    
    # Model SMART (70B) cho văn phong tự nhiên
    system_instr = "You are a friendly conversational assistant. Ask short, clear and natural questions."
    
    # Mặc định là smart nên chỉ cần truyền system_instruction
    return generate_response(prompt, system_instruction=system_instr)