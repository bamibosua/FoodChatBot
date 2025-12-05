import spacy

NLPModule = spacy.load('./NLPModule/custom_ner_model')

def nerExtractor(input: str):
    doc = NLPModule(input.lower())
    location = "null"
    taste = []
    budget = "null"
    food = []
    city = "null"

    for ent in doc.ents:
        if ent.label_ == 'LOCATION':
            location = ent.text
        elif ent.label_ == 'TASTE':
            taste.append(ent.text)
        elif ent.label_ == 'BUDGET':
            budget = ent.text
        elif ent.label_ == 'FOOD':
            food.append(ent.text)
        elif ent.label_ == 'CITY':
            city = ent.text
            
    print(f'DEBUG: {city} | {budget} | {location} | {taste}')
    return {
        "location": location,
        "tasteAndFood": taste,
        "budget_raw": budget,
        "food": food,
        "city": city
    }