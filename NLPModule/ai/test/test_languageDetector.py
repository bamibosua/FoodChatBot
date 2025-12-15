import pytest

import NLPModule.ai.languageDetector as languageDetector

def test_ai_language_detector_vietnamese(monkeypatch):
    """Test phát hiện tiếng Việt"""
    user_input = "Tôi muốn ăn phở"

    def mock_generate_response(prompt, system_instruction=None):
        return "vi"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "vi"


def test_ai_language_detector_english(monkeypatch):
    """Test phát hiện tiếng Anh"""
    user_input = "I want to eat pizza"

    def mock_generate_response(prompt, system_instruction=None):
        return "en"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "en"


def test_ai_language_detector_japanese(monkeypatch):
    """Test phát hiện tiếng Nhật"""
    user_input = "私は食べたい"

    def mock_generate_response(prompt, system_instruction=None):
        return "ja"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "ja"


def test_ai_language_detector_korean(monkeypatch):
    """Test phát hiện tiếng Hàn"""
    user_input = "나는 먹고 싶어"

    def mock_generate_response(prompt, system_instruction=None):
        return "ko"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "ko"


def test_ai_language_detector_simplified_chinese(monkeypatch):
    """Test phát hiện tiếng Trung giản thể"""
    user_input = "我想吃面"

    def mock_generate_response(prompt, system_instruction=None):
        return "zh-CN"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "zh-CN"


def test_ai_language_detector_traditional_chinese(monkeypatch):
    """Test phát hiện tiếng Trung phồn thể"""
    user_input = "我想吃飯"

    def mock_generate_response(prompt, system_instruction=None):
        return "zh-TW"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "zh-TW"


def test_ai_language_detector_french(monkeypatch):
    """Test phát hiện tiếng Pháp"""
    user_input = "Je veux manger"

    def mock_generate_response(prompt, system_instruction=None):
        return "fr"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "fr"


def test_ai_language_detector_spanish(monkeypatch):
    """Test phát hiện tiếng Tây Ban Nha"""
    user_input = "Quiero comer paella"

    def mock_generate_response(prompt, system_instruction=None):
        return "es"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "es"


def test_ai_language_detector_german(monkeypatch):
    """Test phát hiện tiếng Đức"""
    user_input = "Ich möchte essen"

    def mock_generate_response(prompt, system_instruction=None):
        return "de"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "de"


def test_ai_language_detector_thai(monkeypatch):
    """Test phát hiện tiếng Thái"""
    user_input = "ฉันอยากกินข้าว"

    def mock_generate_response(prompt, system_instruction=None):
        return "th"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "th"


def test_ai_language_detector_indonesian(monkeypatch):
    """Test phát hiện tiếng Indonesia"""
    user_input = "Saya ingin makan nasi goreng"

    def mock_generate_response(prompt, system_instruction=None):
        return "id"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "id"


def test_ai_language_detector_russian(monkeypatch):
    """Test phát hiện tiếng Nga"""
    user_input = "Я хочу есть"

    def mock_generate_response(prompt, system_instruction=None):
        return "ru"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "ru"


def test_ai_language_detector_arabic(monkeypatch):
    """Test phát hiện tiếng Ả Rập"""
    user_input = "أريد أن آكل"

    def mock_generate_response(prompt, system_instruction=None):
        return "ar"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "ar"


def test_ai_language_detector_portuguese(monkeypatch):
    """Test phát hiện tiếng Bồ Đào Nha"""
    user_input = "Eu quero comer feijoada"

    def mock_generate_response(prompt, system_instruction=None):
        return "pt"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "pt"


def test_ai_language_detector_hindi(monkeypatch):
    """Test phát hiện tiếng Hindi"""
    user_input = "मैं खाना चाहता हूं"

    def mock_generate_response(prompt, system_instruction=None):
        return "hi"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "hi"


def test_ai_language_detector_mixed_english_vietnamese(monkeypatch):
    """Test phát hiện ngôn ngữ hỗn hợp (chủ yếu tiếng Việt)"""
    user_input = "Tôi muốn ăn pizza ở Quận 1"

    def mock_generate_response(prompt, system_instruction=None):
        return "vi"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "vi"


def test_ai_language_detector_only_numbers(monkeypatch):
    """Test với input chỉ có số"""
    user_input = "100k"

    def mock_generate_response(prompt, system_instruction=None):
        return "en"  # Default to English for numbers

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "en"


def test_ai_language_detector_location_only(monkeypatch):
    """Test với input chỉ có địa điểm (tiếng Việt)"""
    user_input = "Quận 1"

    def mock_generate_response(prompt, system_instruction=None):
        return "vi"

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "vi"


def test_ai_language_detector_empty_string(monkeypatch):
    """Test với chuỗi rỗng"""
    user_input = ""

    def mock_generate_response(prompt, system_instruction=None):
        return "en"  # Default language

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "en"


def test_ai_language_detector_special_characters(monkeypatch):
    """Test với ký tự đặc biệt"""
    user_input = "!@#$%^&*()"

    def mock_generate_response(prompt, system_instruction=None):
        return "en"  # Default to English for special chars

    monkeypatch.setattr(
        languageDetector,
        "generate_response",
        mock_generate_response
    )

    result = languageDetector.ai_language_detector(user_input)
    assert result == "en"