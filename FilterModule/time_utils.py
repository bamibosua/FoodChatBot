# time_utils.py
import re
from datetime import datetime, timedelta

# --- HELPER MỚI: Dịch Thứ sang Tiếng Việt (Lowercase) ---
def get_vietnamese_day(dt_obj):
    """Map weekday index (0=Monday) to Vietnamese lowercase day names."""
    days_mapping = {
        0: "thứ hai", 1: "thứ ba", 2: "thứ tư", 3: "thứ năm", 
        4: "thứ sáu", 5: "thứ bảy", 6: "chủ nhật"
    }
    return days_mapping[dt_obj.weekday()]

def parse_time(time_str):
    """
    Chuyển chuỗi giờ (HH:MM) thành đối tượng time.
    FIX: Sử dụng format 24 giờ (%H:%M) thay vì 12 giờ AM/PM.
    """
    if not time_str:
        return None
    
    try:
        clean_str = time_str.strip()
        # Dùng %H:%M cho format 24 giờ
        return datetime.strptime(clean_str, "%H:%M").time() 
    except ValueError:
        return None

def is_time_in_range(current, start, end):
    """Kiểm tra xem current có nằm trong khoảng start -> end không."""
    if start <= end:
        return start <= current <= end
    else:
        # Qua đêm (VD: 22:00 - 02:00)
        return start <= current or current <= end

def is_restaurant_open(restaurant_data, check_time=None, check_day=None):
    """
    Kiểm tra quán có mở cửa không.
    Dùng check_day (Tiếng Việt lowercase) để so khớp với operating_hours.
    """
    # 1. Xác định thời gian và ngày kiểm tra (Sử dụng Tiếng Việt)
    if check_time and check_day:
        current_time_obj = check_time
        current_day = check_day.lower() # Giả định đã là Tiếng Việt/lowercase
    else:
        now = datetime.now()
        current_time_obj = now.time()
        current_day = get_vietnamese_day(now) # FIX: Lấy thứ Tiếng Việt
        
    today_date = datetime.now().date()
    current_dt = datetime.combine(today_date, current_time_obj)

    # 2. Kiểm tra dữ liệu và ngày hiện tại
    operating_hours = restaurant_data.get('operating_hours')
    if not operating_hours:
        # Fallback logic cũ (chỉ kiểm tra open_state nếu không có operating_hours)
        if 'open_state' in restaurant_data:
            open_state = restaurant_data['open_state'].lower()
            if 'đang mở cửa' in open_state: # Dùng Tiếng Việt thay vì English
                return True, 9999
            elif 'đóng cửa' in open_state: 
                return False, 0
        return True, 9999
        
    # FIX: current_day (Tiếng Việt) phải là key trong operating_hours
    if current_day not in operating_hours:
        # Nếu không tìm thấy ngày (Lỗi data), mặc định Đóng
        return False, 0
    
    hours_today = operating_hours[current_day]
    
    # ❌ LỖI: if 'đóng cửa' in hours_today.lower(): pass 
    
    # ✅ SỬA LẠI:
    # Nếu có chữ "Đóng cửa" hoặc "Closed" và KHÔNG có số nào -> Return False
    if ('đóng cửa' in hours_today.lower() or 'closed' in hours_today.lower()) and not any(c.isdigit() for c in hours_today):
        return False, 0 # Trả về Đóng cửa ngay lập tức

    if hours_today == "00:00–00:00": 
        return True, 9999
    
    # 3. Duyệt các khung giờ
    time_ranges = hours_today.split(', ')
    max_minutes_left = 0
    
    for time_range in time_ranges:
        # Sử dụng re.split(r'[–-]', ...) để tách giờ mở và đóng
        parts = re.split(r'[–-]', time_range.strip())
        
        if len(parts) == 2:
            open_time_str = parts[0].strip()
            close_time_str = parts[1].strip()
            
            open_time = parse_time(open_time_str)
            close_time = parse_time(close_time_str)
            
            if open_time and close_time:
                # A. Kiểm tra xem có đang nằm trong giờ mở cửa không
                if is_time_in_range(current_time_obj, open_time, close_time):
                    
                    # Tạo datetime cho giờ đóng cửa
                    close_dt = datetime.combine(today_date, close_time)
                    
                    # Xử lý trường hợp qua đêm
                    if close_time < open_time:
                        if current_time_obj >= open_time:
                             # Nếu đang ở khung tối muộn (VD 23:00), giờ đóng cửa là ngày hôm sau
                            close_dt += timedelta(days=1)
                        # else: Nếu đang ở khung sáng sớm (VD 01:00), close_dt đã đúng ngày
                        
                    # Tính thời gian còn lại
                    diff = close_dt - current_dt
                    minutes_left = diff.total_seconds() / 60
                    
                    # B. Kiểm tra 30 phút còn lại
                    if minutes_left > 30:
                        return True, int(minutes_left) 
                    else:
                        # Gần đóng cửa, ghi nhận và check khung giờ tiếp theo
                        max_minutes_left = max(max_minutes_left, int(minutes_left))
                        continue 
                        
    # 4. Quyết định cuối cùng
    # Nếu không tìm thấy khung giờ nào mở, trả về Đóng
    return False, max_minutes_left


def filter_open_restaurants(local_results, check_time=None, check_day=None):
    """Lọc danh sách quán đang mở cửa - TRẢ VỀ MẢNG DICT"""
    open_restaurants = []
    processed_restaurants = []
    
    check_time_obj = None
    check_day_str = None
    
    # 1. Chuẩn bị thời gian (Sử dụng logic Tiếng Việt)
    now = datetime.now()
    if check_time:
        try:
            # FIX: Dùng %H:%M (24h) để parse input của user
            check_time_obj = datetime.strptime(check_time, "%H:%M").time()
            print(f"⏰ Kiểm tra thời gian: {check_time}")
        except ValueError:
            check_time_obj = now.time()
            print(f"⏰ Dùng thời gian hiện tại")
    else:
        check_time_obj = now.time()
        
    if check_day:
        check_day_str = check_day.lower() # Phải là Tiếng Việt lowercase
        print(f"📅 Kiểm tra ngày: {check_day_str}")
    else:
        check_day_str = get_vietnamese_day(now) # FIX: Lấy thứ Tiếng Việt
        print(f"📅 Dùng ngày hiện tại: {check_day_str}")
        
    print(f"📊 Tổng số nhà hàng đầu vào: {len(local_results)}")
    
    for restaurant in local_results:
        is_open, minutes_left = is_restaurant_open(
            restaurant, 
            check_time=check_time_obj, 
            check_day=check_day_str
        )
        
        restaurant_copy = restaurant.copy()
        
        # Gắn nhãn trạng thái vào Dictionary của quán (Không loại bỏ)
        restaurant_copy['is_currently_open'] = is_open 
        restaurant_copy['minutes_left'] = minutes_left
        processed_restaurants.append(restaurant_copy)

        # Xóa các lệnh in/append cũ trong block if is_open: (nếu có)
    
    # In ra số lượng để debug
    open_count = sum(1 for r in processed_restaurants if r.get('is_currently_open'))
    print(f"📊 {open_count} quán mở, {len(processed_restaurants) - open_count} quán đóng đã được gắn nhãn.")
            
    return processed_restaurants # TRẢ VỀ TẤT CẢ