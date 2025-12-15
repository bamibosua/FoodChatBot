import re

# Giữ nguyên hàm cũ nếu cần dùng chỗ khác
def parse_price(price_str):
    rng = parse_price_range(price_str)
    return rng[1] if rng else None

def parse_price_range(price_str):
    """
    Trả về tuple (min_price, max_price).
    Ví dụ: 
    - "20k - 50k" -> (20000, 50000)
    - "30k"       -> (30000, 30000)
    - "$$"        -> (50000, 150000) (Ước lượng)
    """
    if not price_str: return None
    
    # 1. Xử lý Price Level (Symbol) của Google Maps
    if '$$$$' in price_str: return (500000, 2000000) # Hạng sang
    if '$$$' in price_str:  return (200000, 500000)  # Đắt
    if '$$' in price_str:   return (50000, 200000)   # Trung bình
    if '$' in price_str:    return (0, 50000)        # Rẻ
    
    # 2. Xử lý chuỗi số (giống logic cũ nhưng lấy hết các số)
    raw_str = price_str.lower().replace(',', '.')
    try:
        matches = re.findall(r'(\d+(?:\.\d+)?)\s*(k)?', raw_str)
        parsed_prices = []
        
        for num_str, unit in matches:
            val = 0.0
            is_thousand_sep = False
            if '.' in num_str:
                parts = num_str.split('.')
                if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
                    is_thousand_sep = True
            
            if is_thousand_sep: val = float(num_str.replace('.', ''))
            else: val = float(num_str)
            
            if unit == 'k' or val < 1000: val *= 1000
            parsed_prices.append(int(val))
            
        if not parsed_prices: return None
        
        # 3. Trả về (Min, Max)
        # Nếu chỉ tìm thấy 1 số (vd: "35k") -> Min=35k, Max=35k
        if len(parsed_prices) == 1:
            return (parsed_prices[0], parsed_prices[0])
            
        return (min(parsed_prices), max(parsed_prices))
    
    except Exception:
        return None