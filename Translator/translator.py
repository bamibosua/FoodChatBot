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
    try:
        return GoogleTranslator(source='auto', target=dest_lang).translate(text)
    except Exception:
        return text  # fallback
    
