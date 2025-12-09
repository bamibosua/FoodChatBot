from Translator.translator import translate_text

def normalizeFields(AIExtractor: dict):
    location = AIExtractor.get("location")
    # taste = AIExtractor.get("tasteAndFood")
    foods = AIExtractor.get("foods")
    budget = AIExtractor.get("budget_raw")
    city = AIExtractor.get("city")

    if location in ("null", "", None): location = None
    # if not isinstance(taste, list): taste = []
    if not isinstance(foods, list): foods = []
    if budget in ("null", "", None): budget = None
    if city in ("null", "", None): city = "hcm"

    print(f'DEBUG: {city} | {budget} | {location} | {foods}')
    
    return {
        "location": translate_text(location, 'vi'),
        "city": translate_text(city, 'vi'),
        "foods": translate_text(foods, 'vi'),
        "budget": budget,
    }