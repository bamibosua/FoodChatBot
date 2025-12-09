from .client import generate_response
from .promptBuilder import buildFixUserSpellingPrompt

def AIFixSpellingErrors(userInput: str):
    prompt = buildFixUserSpellingPrompt(userInput)
    return generate_response(prompt)