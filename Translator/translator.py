from deep_translator import GoogleTranslator
from lingua import LanguageDetectorBuilder


# Tạo detector
_detector = LanguageDetectorBuilder.from_all_languages().build()

def detect_language(text: str) -> str:
    """
    Detect ngôn ngữ của đoạn text đầu vào.
    """
    lang = _detector.detect_language_of(text)
    if lang is None:
        return "unknown"

    # Có ngôn ngữ không có mã → unknown
    iso = lang.iso_code_639_1
    if iso is None:
        return "unknown"

    return iso.name.lower()

def get_original_language(text: str) -> str:
    return detect_language(text)

def translate_text(text: str, dest_lang: str) -> str:
    """
    Translate text to destination language.
    """
    try:
        return GoogleTranslator(source='auto', target=dest_lang).translate(text)
    except Exception:
        return text  # back to original text if translation fails