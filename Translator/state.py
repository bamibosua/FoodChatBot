# state.py
_current_lang = None


def set_lang(lang: str):
    """Cập nhật ngôn ngữ người dùng."""
    global _current_lang
    _current_lang = lang


def get_lang() -> str:
    """Lấy ngôn ngữ hiện tại; fallback = None."""
    return _current_lang
