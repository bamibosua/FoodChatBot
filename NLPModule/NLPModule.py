from NLPModule.ai.fixSpelling import AIFixSpellingErrors
from NLPModule.ai.AIForMissingFields import aiReplyForMissingFields
from NLPModule.ai.replyForUser import replyForUser
from NLPModule.ner.extractor import nerExtractor
from NLPModule.ner.normalize import normalizeFields
from NLPModule.utils.checkIsInHCM import isInHCM
from Translator.translator import translate_text, get_original_language

def isInHCMMain(city: str):
    return isInHCM(city)
    

def analyzeUserInput(userInput: str):
    # phát hiện ngôn ngữ gốc
    original_lang = get_original_language(userInput)
    fixedInput = AIFixSpellingErrors(userInput)

    # dịch sang tiếng anh
    if original_lang != 'en':
        fixedInput = translate_text(fixedInput, 'en')

    rawExtraction = nerExtractor(fixedInput)
    normalized = normalizeFields(rawExtraction)
    
    #test
    # print(original_lang)

    return normalized
    
def replyMissingFields(missingFields, currentData, original_lang):
    prompt = aiReplyForMissingFields(missingFields, currentData)
    if(original_lang != 'en'):
        prompt = translate_text(prompt, dest_lang=original_lang)
    return prompt

def reply(data, original_lang):
    answer = replyForUser(data)  # sinh câu trả lời bằng tiếng Anh
    # dịch ngược về ngôn ngữ gốc
    
    if original_lang != 'en':
        answer_translated = translate_text(answer, dest_lang=original_lang)
        return answer_translated
    return answer