import pytest
import json

import NLPModule.ai.aiExtractor as aiExtractor

def test_ai_extractor_with_realistic_input(monkeypatch):
    """Test với input thực tế đầy đủ thông tin"""
    user_input = (
        "Tôi muốn ăn cơm tấm ở 214 Nguyễn Trãi, Nguyễn Cư Trinh "
        "Quận 1 Hồ Chí Minh, ngân sách là 100k"
    )

    expected_output = {
        "location": "214 Nguyễn Trãi, Nguyễn Cư Trinh, Quận 1, Hồ Chí Minh",
        "foods": ["cơm tấm"],
        "budget": "100k",
        "taste": ["ăn"]
    }

    def mock_generate_response(prompt, system_instr):
        return expected_output

    monkeypatch.setattr(
        aiExtractor,
        "generate_response",
        mock_generate_response
    )

    result = aiExtractor.aiExtractor(user_input)
    assert result == expected_output


def test_ai_extractor_only_food(monkeypatch):
    """Test khi chỉ có thông tin món ăn"""
    user_input = "tôi muốn ăn phở"

    expected_output = {
        "location": "",
        "foods": ["phở"],
        "budget": "",
        "taste": ["ăn"]
    }

    def mock_generate_response(prompt, system_instr):
        return expected_output

    monkeypatch.setattr(
        aiExtractor,
        "generate_response",
        mock_generate_response
    )

    result = aiExtractor.aiExtractor(user_input)
    assert result == expected_output


def test_ai_extractor_only_location_and_budget(monkeypatch):
    """Test khi chỉ có địa điểm và ngân sách"""
    user_input = "tìm quán ở quận 1 dưới 50k"

    expected_output = {
        "location": "Quận 1",
        "foods": [],
        "budget": "dưới 50k",
        "taste": []
    }

    def mock_generate_response(prompt, system_instr):
        return expected_output

    monkeypatch.setattr(
        aiExtractor,
        "generate_response",
        mock_generate_response
    )

    result = aiExtractor.aiExtractor(user_input)
    assert result == expected_output


def test_ai_extractor_with_taste_only(monkeypatch):
    """Test khi chỉ có thông tin vị"""
    user_input = "muốn uống gì đó chua chua ngọt ngọt"

    expected_output = {
        "location": "",
        "foods": [],
        "budget": "",
        "taste": ["chua chua", "ngọt ngọt"]
    }

    def mock_generate_response(prompt, system_instr):
        return expected_output

    monkeypatch.setattr(
        aiExtractor,
        "generate_response",
        mock_generate_response
    )

    result = aiExtractor.aiExtractor(user_input)
    assert result == expected_output


def test_ai_extractor_multiple_foods(monkeypatch):
    """Test với nhiều món ăn"""
    user_input = "tìm quán có phở, bún bò, bánh mì ở quận 3"

    expected_output = {
        "location": "Quận 3",
        "foods": ["phở", "bún bò", "bánh mì"],
        "budget": "",
        "taste": []
    }

    def mock_generate_response(prompt, system_instr):
        return expected_output

    monkeypatch.setattr(
        aiExtractor,
        "generate_response",
        mock_generate_response
    )

    result = aiExtractor.aiExtractor(user_input)
    assert result == expected_output


def test_ai_extractor_with_foreign_currency(monkeypatch):
    """Test chuyển đổi ngoại tệ"""
    user_input = "tìm quán ăn khoảng 4 usd ở quận 1"

    expected_output = {
        "location": "Quận 1",
        "foods": [],
        "budget": "100k",
        "taste": ["ăn"]
    }

    def mock_generate_response(prompt, system_instr):
        return expected_output

    monkeypatch.setattr(
        aiExtractor,
        "generate_response",
        mock_generate_response
    )

    result = aiExtractor.aiExtractor(user_input)
    assert result == expected_output


def test_ai_extractor_empty_input(monkeypatch):
    """Test với input rỗng"""
    user_input = ""

    expected_output = {
        "location": "",
        "foods": [],
        "budget": "",
        "taste": []
    }

    def mock_generate_response(prompt, system_instr):
        return expected_output

    monkeypatch.setattr(
        aiExtractor,
        "generate_response",
        mock_generate_response
    )

    result = aiExtractor.aiExtractor(user_input)
    assert result == expected_output


def test_ai_extractor_with_range_budget(monkeypatch):
    """Test với ngân sách dạng khoảng"""
    user_input = "tìm quán cà phê từ 50k đến 100k ở quận 2"

    expected_output = {
        "location": "Quận 2",
        "foods": ["cà phê"],
        "budget": "50k-100k",
        "taste": []
    }

    def mock_generate_response(prompt, system_instr):
        return expected_output

    monkeypatch.setattr(
        aiExtractor,
        "generate_response",
        mock_generate_response
    )

    result = aiExtractor.aiExtractor(user_input)
    assert result == expected_output


def test_ai_extractor_complex_location(monkeypatch):
    """Test với địa chỉ phức tạp"""
    user_input = "quán ăn ở 123 Lê Lợi, Phường Bến Thành, Quận 1, TP.HCM"

    expected_output = {
        "location": "123 Lê Lợi, Phường Bến Thành, Quận 1, TP.HCM",
        "foods": [],
        "budget": "",
        "taste": ["ăn"]
    }

    def mock_generate_response(prompt, system_instr):
        return expected_output

    monkeypatch.setattr(
        aiExtractor,
        "generate_response",
        mock_generate_response
    )

    result = aiExtractor.aiExtractor(user_input)
    assert result == expected_output


def test_ai_extractor_with_all_fields(monkeypatch):
    """Test với tất cả các trường đều có dữ liệu"""
    user_input = "tìm quán bún chả cay cay ở Gò Vấp dưới 60k"

    expected_output = {
        "location": "Gò Vấp",
        "foods": ["bún chả"],
        "budget": "dưới 60k",
        "taste": ["cay cay"]
    }

    def mock_generate_response(prompt, system_instr):
        return expected_output

    monkeypatch.setattr(
        aiExtractor,
        "generate_response",
        mock_generate_response
    )

    result = aiExtractor.aiExtractor(user_input)
    assert result == expected_output