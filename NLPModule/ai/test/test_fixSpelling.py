import pytest
import NLPModule.ai.fixSpelling as fixSpelling
def test_ai_fix_spelling_remove_filler_words(monkeypatch):
    """Test loại bỏ filler words"""
    user_input = "tôi muốn uống gì đó chua chua lại"

    def mock_generate_response(prompt, system_instruction=None):
        return "uống chua chua"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "uống chua chua"


def test_ai_fix_spelling_convert_written_numbers(monkeypatch):
    """Test chuyển đổi số từ chữ sang số"""
    user_input = "tôi muốn ăn phở quận 1 khoảng một trăm k"

    def mock_generate_response(prompt, system_instruction=None):
        return "ăn phở quận 1 100k"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "ăn phở quận 1 100k"


def test_ai_fix_spelling_keep_location_intact(monkeypatch):
    """Test giữ nguyên địa điểm"""
    user_input = "tìm quán bún chả ở gò vấp dưới 50k"

    def mock_generate_response(prompt, system_instruction=None):
        return "bún chả gò vấp dưới 50k"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "bún chả gò vấp dưới 50k"


def test_ai_fix_spelling_simplify_sentence(monkeypatch):
    """Test đơn giản hóa câu"""
    user_input = "cho tôi quán cà phê ở quận 3"

    def mock_generate_response(prompt, system_instruction=None):
        return "cà phê quận 3"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "cà phê quận 3"


def test_ai_fix_spelling_budget_only(monkeypatch):
    """Test với chỉ có ngân sách"""
    user_input = "ngân sách của tôi là 100k"

    def mock_generate_response(prompt, system_instruction=None):
        return "100k"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "100k"


def test_ai_fix_spelling_usd_to_vnd(monkeypatch):
    """Test chuyển đổi USD sang VND"""
    user_input = "tìm quán ăn khoảng 4 usd"

    def mock_generate_response(prompt, system_instruction=None):
        return "ăn 100k"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "ăn 100k"


def test_ai_fix_spelling_dollars_to_vnd(monkeypatch):
    """Test chuyển đổi dollars sang VND"""
    user_input = "muốn ăn gì đó khoảng 10 dollars"

    def mock_generate_response(prompt, system_instruction=None):
        return "ăn 250k"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "ăn 250k"


def test_ai_fix_spelling_rmb_to_vnd(monkeypatch):
    """Test chuyển đổi RMB sang VND"""
    user_input = "budget 30 rmb"

    def mock_generate_response(prompt, system_instruction=None):
        return "105k"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "105k"


def test_ai_fix_spelling_baht_to_vnd(monkeypatch):
    """Test chuyển đổi Baht sang VND"""
    user_input = "quán cà phê dưới 100 baht"

    def mock_generate_response(prompt, system_instruction=None):
        return "cà phê dưới 143k"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "cà phê dưới 143k"


def test_ai_fix_spelling_euro_to_vnd(monkeypatch):
    """Test chuyển đổi Euro sang VND"""
    user_input = "tìm quán 4 euro"

    def mock_generate_response(prompt, system_instruction=None):
        return "108k"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "108k"


def test_ai_fix_spelling_keep_chua_chua(monkeypatch):
    """Test giữ nguyên 'chua chua' không thêm 'nước'"""
    user_input = "tìm đồ uống chua chua"

    def mock_generate_response(prompt, system_instruction=None):
        return "uống chua chua"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "uống chua chua"
    assert "nước" not in result


def test_ai_fix_spelling_keep_pho(monkeypatch):
    """Test giữ nguyên 'phở' không thêm 'ở'"""
    user_input = "muốn ăn phở"

    def mock_generate_response(prompt, system_instruction=None):
        return "ăn phở"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "ăn phở"


def test_ai_fix_spelling_convert_large_numbers(monkeypatch):
    """Test chuyển đổi số lớn sang format k"""
    user_input = "ngân sách 100000"

    def mock_generate_response(prompt, system_instruction=None):
        return "100k"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "100k"


def test_ai_fix_spelling_input_as_list(monkeypatch):
    """Test với input là list"""
    user_input = ["tôi", "muốn", "ăn", "phở"]

    def mock_generate_response(prompt, system_instruction=None):
        return "ăn phở"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "ăn phở"


def test_ai_fix_spelling_remove_markdown(monkeypatch):
    """Test loại bỏ markdown từ response"""
    user_input = "ăn phở quận 1"

    def mock_generate_response(prompt, system_instruction=None):
        return "```python\năn phở quận 1\n```"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "ăn phở quận 1"
    assert "```" not in result


def test_ai_fix_spelling_remove_quotes(monkeypatch):
    """Test loại bỏ quotes từ response"""
    user_input = "cà phê quận 3"

    def mock_generate_response(prompt, system_instruction=None):
        return '"cà phê quận 3"'

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "cà phê quận 3"
    assert '"' not in result


def test_ai_fix_spelling_remove_brackets(monkeypatch):
    """Test loại bỏ brackets từ response"""
    user_input = "bún chả gò vấp"

    def mock_generate_response(prompt, system_instruction=None):
        return '["bún chả gò vấp"]'

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "bún chả gò vấp"
    assert "[" not in result and "]" not in result


def test_ai_fix_spelling_spelling_errors(monkeypatch):
    """Test sửa lỗi chính tả"""
    user_input = "muốn ănnn phởởở quậnn 1"

    def mock_generate_response(prompt, system_instruction=None):
        return "ăn phở quận 1"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "ăn phở quận 1"


def test_ai_fix_spelling_complex_sentence(monkeypatch):
    """Test với câu phức tạp"""
    user_input = "tôi muốn tìm quán bún bò huế cay cay ở quận 5 khoảng 5 dollars"

    def mock_generate_response(prompt, system_instruction=None):
        return "bún bò huế cay cay quận 5 125k"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "bún bò huế cay cay quận 5 125k"


def test_ai_fix_spelling_empty_input(monkeypatch):
    """Test với input rỗng"""
    user_input = ""

    def mock_generate_response(prompt, system_instruction=None):
        return ""

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == ""


def test_ai_fix_spelling_only_location(monkeypatch):
    """Test với chỉ có địa điểm"""
    user_input = "tôi ở quận 1"

    def mock_generate_response(prompt, system_instruction=None):
        return "quận 1"

    monkeypatch.setattr(
        fixSpelling,
        "generate_response",
        mock_generate_response
    )

    result = fixSpelling.AIFixSpellingErrors(user_input)
    assert result == "quận 1"