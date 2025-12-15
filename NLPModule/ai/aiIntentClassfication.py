from .client import generate_response
from .promptBuilder import buildGetUserIntent

def aiIntentClassification(data):
    prompt = buildGetUserIntent(data)
    
    # Model SMART (70B) cho lời khuyên ấm áp, tự nhiên
    system_instr = "You are a food intent classifier."
    
    return generate_response(prompt, system_instruction=system_instr)