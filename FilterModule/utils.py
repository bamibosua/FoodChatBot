import re
from math import radians, cos, sin, asin, sqrt
from datetime import datetime, timedelta
import config

def geocode_location(location: str):
    location = location.strip()
    if not location:
        raise ValueError("Location không được để trống")
    
    loc_lower = location.lower()
    for key, coord in config.DISTRICT_CENTERS.items():
        if key.lower() in loc_lower or loc_lower in key.lower():
            return coord
    
    return config.DISTRICT_CENTERS["District 1"]

# Hàm công thức tính tọa độ
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return round(R * c, 3)

# Hàm thời gian
def parse_hhmm(s: str):
    s = s.strip().replace(" ", "")
    if s == "24:00":
        return datetime.strptime("00:00", "%H:%M").time(), True
    try:
        return datetime.strptime(s, "%H:%M").time(), False
    except ValueError:
        return datetime.strptime("00:00", "%H:%M").time(), False

# Hàm check quán còn mở cửa hay không
def is_open(time_range: str, current_time: str, min_open_minutes: int = 30):
    try:
        if not isinstance(time_range, str) or not time_range.strip():
            return True, 9999

        now_time = datetime.strptime(current_time.strip(), "%H:%M").time()
        today = datetime.today()
        now_dt = datetime.combine(today, now_time)

        periods = [p.strip() for p in time_range.split(",") if p.strip()]
        minutes_left_list = []

        for period in periods:
            if '-' not in period: continue
            parts = re.split(r'\s*[-–—]\s*', period)
            if len(parts) != 2: continue

            open_time, open_is_24 = parse_hhmm(parts[0])
            close_time, close_is_24 = parse_hhmm(parts[1])

            if open_is_24: open_time = datetime.strptime("00:00", "%H:%M").time()
            if close_is_24: close_time = datetime.strptime("00:00", "%H:%M").time()

            open_dt = datetime.combine(today, open_time)
            close_dt = datetime.combine(today, close_time)

            if close_dt <= open_dt:
                close_dt += timedelta(days=1)

            for day_offset in [-1, 0, 1]:
                check_open = open_dt + timedelta(days=day_offset)
                check_close = close_dt + timedelta(days=day_offset)
                
                if check_open <= now_dt <= check_close:
                    minutes_left = (check_close - now_dt).total_seconds() / 60
                    if minutes_left >= min_open_minutes:
                        return True, minutes_left
                    else:
                        minutes_left_list.append(minutes_left)

        return (False, max(minutes_left_list)) if minutes_left_list else (False, 0)
            
    except Exception:
        return True, 9999

# Bộ lọc giá theo 2 trường hợp, 1 giá và khoảng giá (min-max)
def parse_price(raw):
    if not raw:
        return None

    # Chuyển về chuỗi thường, xóa khoảng trắng đầu đuôi
    s = str(raw).lower().strip()

    # --- CASE 1: Xử lý input kiểu "100k", "1.5k", "50k - 100k" ---
    if 'k' in s:
        # Cắt lấy phần trước chữ 'k' đầu tiên (để xử lý dạng khoảng giá 50k-100k -> lấy 50)
        first_part = s.split('k')[0]
        
        # Giữ lại số và dấu chấm/phẩy (để xử lý số thập phân 1.5)
        clean_num = re.sub(r'[^\d.,]', '', first_part).replace(',', '.')
        
        try:
            # Nhân 1000 -> ép kiểu int
            return int(float(clean_num) * 1000)
        except ValueError:
            return None

    # --- CASE 2: Xử lý input kiểu full số "100.000", "100,000", "100.000đ" ---
    # Logic cũ của bạn: Xóa hết dấu chấm phẩy để nối số lại
    s = s.replace("đ", "").replace("vnd", "")
    s = s.replace(".", "").replace(",", "") 
    
    nums = re.findall(r'\d+', s)
    if not nums:
        return None

    # Lấy số đầu tiên tìm thấy
    return int(nums[0])
