from .client import generate_response
from NLPModule.promptBuilder import buildReplyForUserPrompt

def replyForUser(data: dict):
    prompt = buildReplyForUserPrompt(data)
    return generate_response(prompt)