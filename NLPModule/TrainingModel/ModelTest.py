import spacy
from NLPModule.ai.fixSpelling import AIFixSpellingErrors

trained_nlp = spacy.load('./NLPModule/custom_ner_model')

text_tests = [
    "What to eat in thu duc, budget at about 40k-50k?",
    "I want to eat spicy food in district 2 at arround 100k-200k",
    "I’m thinking about that place where the atmosphere sort of feels like a quiet pause in the day, and the food has that kind of comforting ‘you’ll-know-it-when-you-taste-it’ vibe — any idea what spot might fit that mood?"
]
proTexts = AIFixSpellingErrors(text_tests)   # chỉ 1 request API

for text in proTexts:                        # loop từng câu đã sửa
    doc = trained_nlp(text)
    print("Text:", text)
    print("Entities:", [(ent.text, ent.label_) for ent in doc.ents])