from deep_translator import GoogleTranslator
from lingua import LanguageDetectorBuilder
from Translator.utils import is_number_plus_k
from Translator.state import get_lang, set_lang
# Tạo detector 1 lần (tối ưu hiệu suất)
_detector = LanguageDetectorBuilder.from_all_languages().build()


def detect_language(text: str) -> str:
    """
    Detect language of the input.
    """
    lang = _detector.detect_language_of(text)
    if lang is None:
        return "unknown"

    # Lấy ISO 639-1; có ngôn ngữ không có mã → fallback
    iso = lang.iso_code_639_1
    if iso is None:
        return "unknown"

    return iso.name.lower()

def get_original_language(text: str) -> str:
    return detect_language_safe(text)

def translate_text(text: str, dest_lang: str) -> str:
    """
    Translate text to destination language.
    """
    try:
        return GoogleTranslator(source='auto', target=dest_lang).translate(text)
    except Exception:
        return text  # fallback
    
def detect_language_safe(text: str) -> str:
    """
    Nếu input là số hoặc số+k/K → không detect → giữ hiện trạng.
    """
    current = get_lang()

    if is_number_plus_k(text) or text.isdigit():
        return current

    lang = _detector.detect_language_of(text)
    if not lang or not lang.iso_code_639_1:
        return current

    new_lang = lang.iso_code_639_1.name.lower()
    set_lang(new_lang)
    return new_lang
