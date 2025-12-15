import re
from datetime import datetime, timedelta

# 1. HELPER FUNCTIONS
def get_vietnamese_day(dt_obj):
    """Map weekday index (0=Monday) to Vietnamese lowercase day names."""
    days_mapping = {
        0: "thứ hai", 1: "thứ ba", 2: "thứ tư", 3: "thứ năm", 
        4: "thứ sáu", 5: "thứ bảy", 6: "chủ nhật"
    }
    return days_mapping[dt_obj.weekday()]

def parse_time(time_str):
    """Chuyển chuỗi giờ (HH:MM) thành đối tượng time (24h format)."""
    if not time_str:
        return None
    
    try:
        clean_str = time_str.strip()
        return datetime.strptime(clean_str, "%H:%M").time() 
    except ValueError:
        return None

def is_time_in_range(current, start, end):
    """Kiểm tra xem current có nằm trong khoảng start -> end không (Hỗ trợ qua đêm)."""
    if start <= end:
        # Khung giờ bình thường (VD: 09:00 - 18:00)
        return start <= current <= end
    else:
        # Khung giờ qua đêm (VD: 22:00 - 02:00)
        return start <= current or current <= end

# 2. MAIN LOGIC: KIỂM TRA QUÁN MỞ CỬA
def is_restaurant_open(restaurant_data, check_time=None, check_day=None):
    """
    Kiểm tra quán có mở cửa không. Logic: Chỉ cần nằm trong khung giờ là MỞ.
    
    Returns:
        (is_open: bool, minutes_left: int)
    """
    # BƯỚC 1: XÁC ĐỊNH THỜI GIAN VÀ NGÀY KIỂM TRA
    if check_time and check_day:
        current_time_obj = check_time
        current_day = check_day.lower()
    else:
        now = datetime.now()
        current_time_obj = now.time()
        current_day = get_vietnamese_day(now)
        
    today_date = datetime.now().date()
    current_dt = datetime.combine(today_date, current_time_obj)

    # BƯỚC 2: KIỂM TRA DỮ LIỆU CƠ BẢN
    operating_hours = restaurant_data.get('operating_hours')
    
    # FALLBACK 1: Không có operating_hours → Dùng open_state
    if not operating_hours:
        if 'open_state' in restaurant_data:
            open_state = restaurant_data['open_state'].lower()
            if any(keyword in open_state for keyword in ['đang mở', 'sắp đóng']):
                return True, 9999
            elif any(keyword in open_state for keyword in ['đã đóng', 'đóng cửa']):
                return False, 0
        return True, 9999 # Mặc định MỞ nếu không có thông tin
    
    # FALLBACK 2: Ngày hiện tại không có trong operating_hours
    if current_day not in operating_hours:
        return False, 0
    
    hours_today = operating_hours[current_day]
    
    # BƯỚC 3: XỬ LÝ CÁC TRƯỜNG HỢP ĐẶC BIỆT
    
    # Case 1: "Đóng cửa" (Toàn bộ ngày nghỉ)
    if re.match(r'^\s*(đóng cửa|closed)\s*$', hours_today.strip(), re.IGNORECASE):
        return False, 0
    
    # Case 2: "00:00–00:00" (Mở cửa 24/7)
    if hours_today.strip() == "00:00–00:00":
        return True, 9999
    
    # BƯỚC 4 & 5: PARSE VÀ KIỂM TRA KHUNG GIỜ
    time_ranges = hours_today.split(', ')
    
    for time_range in time_ranges:
        # Tách giờ mở và giờ đóng (Hỗ trợ cả dấu – và -)
        parts = re.split(r'[–\-]', time_range.strip())
        
        if len(parts) != 2:
            continue
        
        open_time = parse_time(parts[0].strip())
        close_time = parse_time(parts[1].strip())
        
        if not open_time or not close_time:
            continue
        
        # KIỂM TRA: Có đang nằm trong khung giờ này không?
        if is_time_in_range(current_time_obj, open_time, close_time):
            
            # Tính thời gian còn lại (để trả về minutes_left)
            close_dt = datetime.combine(today_date, close_time)
            
            # Xử lý trường hợp qua đêm
            if close_time < open_time:
                if current_time_obj >= open_time:
                    close_dt += timedelta(days=1)
            
            diff = close_dt - current_dt
            minutes_left = diff.total_seconds() / 60
            
            # LOGIC: Chỉ cần đang trong range là MỞ
            return True, int(minutes_left)
            
    # BƯỚC 6: QUYẾT ĐỊNH CUỐI CÙNG
    # Nếu không nằm trong bất kỳ khung giờ nào
    return False, 0 


# 3. FILTER DANH SÁCH 
def filter_open_restaurants(local_results, check_time=None, check_day=None):
    """
    Lọc và gắn nhãn trạng thái mở cửa cho danh sách quán.
    """
    processed_restaurants = []
    
    # BƯỚC 1: CHUẨN BỊ THỜI GIAN KIỂM TRA
    check_time_obj = None
    check_day_str = None
    now = datetime.now()
    
    if check_time:
        try:
            check_time_obj = datetime.strptime(check_time, "%H:%M").time()
            # print(f"⏰ Kiểm tra thời gian: {check_time}") # Bỏ print trong logic
        except ValueError:
            check_time_obj = now.time()
            # print(f"⏰ Format thời gian sai, dùng hiện tại: {now.strftime('%H:%M')}")
    else:
        check_time_obj = now.time()
        # print(f"⏰ Dùng thời gian hiện tại: {now.strftime('%H:%M')}")
    
    if check_day:
        check_day_str = check_day.lower()
        # print(f"📅 Kiểm tra ngày: {check_day_str}")
    else:
        check_day_str = get_vietnamese_day(now)
        # print(f"📅 Dùng ngày hiện tại: {check_day_str}")
    
    # print(f"📊 Tổng số nhà hàng đầu vào: {len(local_results)}")
    
    # BƯỚC 2: DUYỆT VÀ GẮN NHÃN CHO TỪNG QUÁN
    for restaurant in local_results:
        is_open, minutes_left = is_restaurant_open(
            restaurant, 
            check_time=check_time_obj, 
            check_day=check_day_str
        )
        
        restaurant_copy = restaurant.copy()
        
        # Gắn nhãn trạng thái
        restaurant_copy['is_currently_open'] = is_open
        restaurant_copy['minutes_left'] = minutes_left
        
        processed_restaurants.append(restaurant_copy)
    
    # BƯỚC 3: THỐNG KÊ KẾT QUẢ
    open_count = sum(1 for r in processed_restaurants if r.get('is_currently_open'))
    closed_count = len(processed_restaurants) - open_count
    
    # print(f"✅ Kết quả: {open_count} quán MỞ, {closed_count} quán ĐÓNG")
    
    return processed_restaurants