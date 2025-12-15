def is_number_plus_k(text: str) -> bool:
    t = text.strip()
    if not t.lower().endswith("k"):
        return False
    return t[:-1].isdigit()