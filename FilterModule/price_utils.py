import re

def parse_price(price_str):
    """
    Chuẩn hóa chuỗi giá thành số nguyên (lấy giá trị Max/Upper Bound).
    """
    if not price_str:
        return None
    
    # 1. Chuẩn hóa: lowercase, thay phẩy thành chấm để thống nhất xử lý
    # VD: "2,5k" -> "2.5k"
    raw_str = price_str.lower().replace(',', '.')
    
    try:
        # 2. Regex bắt số và đơn vị k
        matches = re.findall(r'(\d+(?:\.\d+)?)\s*(k)?', raw_str)
        
        parsed_prices = []
        for num_str, unit in matches:
            val = 0.0
            
            # --- LOGIC THÔNG MINH XỬ LÝ DẤU CHẤM ---
            # Kiểm tra xem dấu chấm có phải là phân cách hàng nghìn không?
            # Quy tắc: Nếu sau dấu chấm là đúng 3 chữ số (VD: .000, .500) -> Là hàng nghìn
            is_thousand_sep = False
            if '.' in num_str:
                parts = num_str.split('.')
                # Nếu phần đuôi có đúng 3 ký tự (VD: 50.000 hoặc 1.500)
                if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
                    is_thousand_sep = True
            
            if is_thousand_sep:
                # Trường hợp 50.000 -> Xóa chấm -> 50000
                val = float(num_str.replace('.', ''))
            else:
                # Trường hợp 2.5 -> Giữ nguyên chấm -> 2.5
                val = float(num_str)
            
            # --- XỬ LÝ ĐƠN VỊ ---
            if unit == 'k':
                val *= 1000
            elif val < 1000: 
                # Số quá nhỏ (VD: 50, 2.5) -> Nhân 1000
                val *= 1000
                
            parsed_prices.append(int(val))
            
        if not parsed_prices:
            return None
        
        # 3. Trả về giá trị lớn nhất (Upper bound)
        return max(parsed_prices)
    
    except Exception:
        return None