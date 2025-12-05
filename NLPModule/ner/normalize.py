def normalizeFields(AIExtractor: dict):
    location = AIExtractor.get("location")
    taste = AIExtractor.get("tasteAndFood")
    budget = AIExtractor.get("budget_raw")
    food = AIExtractor.get("food")
    city = AIExtractor.get("city")

    if location in ("null", "", None): location = None
    if budget in ("null", "", None): budget = None
    if not isinstance (food, list): food = []
    if city in ("null", "", None): city = "hcm"
    if not isinstance(taste, list): taste = []
    print(f'DEBUG: {city} | {budget} | {location} | {taste}')
    
    return {
        "location": location,
        "taste": taste,
        "budget": budget,
        "foods": food,
        "city": city
    }