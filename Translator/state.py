from deep_translator import GoogleTranslator
from Translator.utils import is_number_plus_k
from Translator.state import get_lang, set_lang
from NLPModule.ai.languageDetector import ai_language_detector

def detect_language(text: str) -> str:
    """
    Detect language of the input.
    """
    return ai_language_detector(text)

def get_original_language(text: str) -> str:
    return detect_language_safe(text)

def translate_text(text: str, dest_lang: str) -> str:
    """
    Translate text to destination language.
    """

    if not text or not text.strip():
        return text
    return GoogleTranslator(source='auto', target=dest_lang).translate(text)
    
def detect_language_safe(text: str) -> str:
    """
    Nếu input là số hoặc số+k/K → không detect → giữ hiện trạng.
    """
    if is_number_plus_k(text) or text.isdigit():
        return get_lang()
    
    detected = detect_language(text)
    set_lang(detected)
    return detected