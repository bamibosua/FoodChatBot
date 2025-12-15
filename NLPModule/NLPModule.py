from NLPModule.ai.fixSpelling import AIFixSpellingErrors
from NLPModule.ai.AIForMissingFields import aiReplyForMissingFields
from NLPModule.ai.replyForUser import replyForUser
from NLPModule.ai.aiReplyRecommend import aiReplyFoodRecommend
from NLPModule.ai.aiIntentClassfication import aiIntentClassification

from NLPModule.ner.extractor import nerExtractor
from NLPModule.ner.normalize import normalizeFields
from Translator.translator import translate_text, get_original_language

from Translator.state import set_lang
    
def analyzeUserInput(userInput: str):
    fixedInput = AIFixSpellingErrors(userInput)
    original_lang = get_original_language(userInput)
    set_lang(original_lang)

    print(f"DEBUG analyzeUserInput: {original_lang}")


    if original_lang != 'vi':
        fixedInput = translate_text(fixedInput, 'vi')
        print(f"DEBUG analyzeUserInput:{fixedInput}")

    raw = nerExtractor(fixedInput)
    normalized = normalizeFields(raw)
    return normalized

def replyMissingFields(missingFields, currentData, original_lang):
    answer = aiReplyForMissingFields(missingFields, currentData)
    if(original_lang != 'en'):
        print(f"Debug reply missing fields reply: {original_lang}")
        answer_translated = translate_text(answer, dest_lang=original_lang)
        return answer_translated
    return answer

def reply(data: dict, original_lang):
    answer = replyForUser(data, original_lang)
    print(f"DEBUG reply language:{original_lang}")

    if original_lang != 'en':
        answer_translated = translate_text(answer, original_lang)
        return answer_translated
    return answer

def replyRecommendFood(data, original_lang):
    answer = aiReplyFoodRecommend(data)
    if original_lang != 'en':
            answer_translated = translate_text(answer, dest_lang=original_lang)
            return answer_translated
    return answer

def userIntentClassification(userInput):
    answer = aiIntentClassification(userInput)

    return answer