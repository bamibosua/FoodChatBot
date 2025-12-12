# Translator/translator.py
from deep_translator import GoogleTranslator
from googletrans import Translator

translator = Translator()
def detect_language(text: str) -> str:
    try:
        return translator.detect(text).lang
    except:
        return 'en'
def get_original_language(text: str) -> str:
    return detect_language(text)

def translate_text(text: str, dest_lang: str) -> str:
    """
    Translate text to destination language.
    """
    translator = Translator()
    try:
        result = translator.translate(text, dest=dest_lang)
        return result.text
    except Exception:
        return text  # fallback
    
