from .client import generate_response
from NLPModule.promptBuilder import buildAskMissingPrompt

def aiReplyForMissingFields(missingFields, currentData):
    prompt = buildAskMissingPrompt(missingFields, currentData)
    return generate_response(prompt)