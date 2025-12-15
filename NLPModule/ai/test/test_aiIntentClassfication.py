import pytest

import NLPModule.ai.aiIntentClassfication as aiIntentClassification

def test_ai_intent_classification_food_with_dish_name(monkeypatch):
    """Test intent Food khi có tên món ăn"""
    user_input = "tôi muốn ăn phở"

    def mock_generate_response(prompt, system_instruction):
        return "Food"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "Food"


def test_ai_intent_classification_food_with_location_only(monkeypatch):
    """Test intent Food khi chỉ có địa điểm"""
    user_input = "Quận 1"

    def mock_generate_response(prompt, system_instruction):
        return "Food"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "Food"


def test_ai_intent_classification_food_with_budget_only(monkeypatch):
    """Test intent Food khi chỉ có ngân sách"""
    user_input = "100k"

    def mock_generate_response(prompt, system_instruction):
        return "Food"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "Food"


def test_ai_intent_classification_food_with_taste(monkeypatch):
    """Test intent Food khi có thông tin vị"""
    user_input = "muốn ăn gì đó cay cay"

    def mock_generate_response(prompt, system_instruction):
        return "Food"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "Food"


def test_ai_intent_classification_food_with_restaurant(monkeypatch):
    """Test intent Food khi tìm nhà hàng"""
    user_input = "tìm quán cà phê"

    def mock_generate_response(prompt, system_instruction):
        return "Food"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "Food"


def test_ai_intent_classification_food_with_location_and_budget(monkeypatch):
    """Test intent Food khi có địa điểm và ngân sách"""
    user_input = "Quận 1 dưới 50k"

    def mock_generate_response(prompt, system_instruction):
        return "Food"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "Food"


def test_ai_intent_classification_not_food_weather(monkeypatch):
    """Test intent NotFood khi hỏi về thời tiết"""
    user_input = "thời tiết hôm nay thế nào?"

    def mock_generate_response(prompt, system_instruction):
        return "NotFood"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "NotFood"


def test_ai_intent_classification_not_food_joke(monkeypatch):
    """Test intent NotFood khi xin kể chuyện cười"""
    user_input = "kể cho tôi một câu chuyện cười"

    def mock_generate_response(prompt, system_instruction):
        return "NotFood"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "NotFood"


def test_ai_intent_classification_not_food_math(monkeypatch):
    """Test intent NotFood khi hỏi toán"""
    user_input = "tính 2 + 2 bằng bao nhiêu?"

    def mock_generate_response(prompt, system_instruction):
        return "NotFood"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "NotFood"


def test_ai_intent_classification_not_food_programming(monkeypatch):
    """Test intent NotFood khi hỏi về lập trình"""
    user_input = "làm thế nào để học Python?"

    def mock_generate_response(prompt, system_instruction):
        return "NotFood"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "NotFood"


def test_ai_intent_classification_not_food_general_knowledge(monkeypatch):
    """Test intent NotFood khi hỏi kiến thức chung"""
    user_input = "ai là tổng thống Mỹ?"

    def mock_generate_response(prompt, system_instruction):
        return "NotFood"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "NotFood"


def test_ai_intent_classification_food_complete_sentence(monkeypatch):
    """Test intent Food với câu đầy đủ"""
    user_input = "tìm quán bún chả cay cay ở Gò Vấp dưới 60k"

    def mock_generate_response(prompt, system_instruction):
        return "Food"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "Food"


def test_ai_intent_classification_food_with_foreign_currency(monkeypatch):
    """Test intent Food với ngoại tệ"""
    user_input = "tìm quán ăn khoảng 4 usd"

    def mock_generate_response(prompt, system_instruction):
        return "Food"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "Food"


def test_ai_intent_classification_food_nearby(monkeypatch):
    """Test intent Food khi tìm quán gần đây"""
    user_input = "quán ăn gần đây"

    def mock_generate_response(prompt, system_instruction):
        return "Food"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "Food"


def test_ai_intent_classification_empty_input(monkeypatch):
    """Test intent với input rỗng"""
    user_input = ""

    def mock_generate_response(prompt, system_instruction):
        return "NotFood"

    monkeypatch.setattr(
        aiIntentClassification,
        "generate_response",
        mock_generate_response
    )

    result = aiIntentClassification.aiIntentClassification(user_input)
    assert result == "NotFood"