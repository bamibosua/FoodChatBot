from .client import generate_response
from .promptBuilder import buildFixUserSpellingPrompt
import json

def AIFixSpellingErrors(userInput: list):
    prompt = buildFixUserSpellingPrompt(userInput)
    return generate_response(prompt)