# NLPModule/ai/aiReplyRecommend.py 
from .client import generate_response
from .promptBuilder import buildFoodRecommendPrompt

def aiReplyFoodRecommend(data):
    prompt = buildFoodRecommendPrompt(data)
    
    # Model SMART (70B) cho lời khuyên ấm áp, tự nhiên
    system_instr = "You are a warm and helpful food recommendation assistant. Keep response short and natural."
    
    return generate_response(prompt, system_instruction=system_instr)