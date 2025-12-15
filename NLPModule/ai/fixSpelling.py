# NLPModule/ai/fixSpelling.py 
from .client import generate_response
from .promptBuilder import buildFixUserSpellingPrompt
import ast

def AIFixSpellingErrors(userInput: list):
    # Convert list to string nếu cần
    if isinstance(userInput, list):
        userInput = ' '.join(userInput)
    
    prompt = buildFixUserSpellingPrompt(userInput)
    
    # Model FAST (8B) cho tốc độ, QUAN TRỌNG: System instruction nghiêm ngặt
    system_instr = "You are a text normalization assistant. Output ONLY the cleaned text. No introduction, no explanation, no markdown."
    
    # GỌI MODEL FAST (8B)
    response = generate_response(prompt, system_instruction=system_instr)
    
    # Clean response
    if not isinstance(response, str):
        response = str(response)
    
    response = response.strip()
    
    # Remove markdown, quotes, brackets...
    if '```' in response:
        response = response.replace('```python', '').replace('```json', '').replace('```', '').strip()
    
    for quote in ['"', "'", '`']:
        if response.startswith(quote) and response.endswith(quote):
            response = response[1:-1]
    
    if response.startswith('[') and response.endswith(']'):
        try:
            parsed = ast.literal_eval(response)
            response = parsed[0] if isinstance(parsed, list) and parsed else response[1:-1]
        except:
            response = response[1:-1]
    
    return response.strip()