from .client import generate_response
from .promptBuilder import buildReplyForUserPrompt

def replyForUser(data: dict):
    prompt = buildReplyForUserPrompt(data)
    return generate_response(prompt)