from Translator.translator import translate_text
import json

def normalizeFields(AIExtractor: dict):
    if isinstance(AIExtractor, str):
        AIExtractor = json.loads(AIExtractor)

    location = AIExtractor.get("location")
    taste = AIExtractor.get("taste")
    foodsRaw = AIExtractor.get("foods")
    budget = AIExtractor.get("budget")

    if location in ("null", "", None): location = None
    if not isinstance(taste, list): taste = []
    if not isinstance(foodsRaw, list): foodsRaw = []
    if budget in ("null", "", None): budget = None

    print(f'DEBUG normalize: {budget} | {foodsRaw} | {location} | {taste}')
    
    foodsTrans = [translate_text(food, 'vi') for food in foodsRaw]
    
    return {
        "location": translate_text(location, 'vi'),
        "foods": foodsTrans,
        "budget": budget,
        "taste": taste
    }