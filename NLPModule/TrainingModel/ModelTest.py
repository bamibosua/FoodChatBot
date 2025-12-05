import spacy

trained_nlp = spacy.load('../custom_ner_model')

text_tests = [
    "What to eat in thu duc, budget at about 40k-50k?",
    "I want to eat spicy food in district 2 at arround 100k-200k",
    "Eat beef at District 3 Ha Noi City about 500k",
    "I want to eat noodles at phu nhuan district arround 100k is good",
    "I want to eat fish noodles at Ho Chi Minh City around one hundred k",
    "Find noodles with pork in District 1 under 100000"
]

for text in text_tests:
    doc = trained_nlp(text)
    print(f'Text: {text}')
    print (f'Entities', [(ent.text, ent.label_) for ent in doc.ents])
    print()