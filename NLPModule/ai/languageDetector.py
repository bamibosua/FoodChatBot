from .client import generate_response
from .promptBuilder import buildGetUserLanguagePrompt


def ai_language_detector(input):
    prompt = buildGetUserLanguagePrompt(input)
    return generate_response(prompt)