# restaurant_service.py
import json
import os
from datetime import datetime
from .data_utils import geocode_location, fetch_places_google_maps
from .filter_utils import filter_and_split_restaurants

# API KEYS CONFIG (Có thể load từ env hoặc file config riêng)
SERP_API_KEY = "27eadbf87685cf226d8f072c5e18315984c9bc869209c2f1c6d676524e579e4d"
GEMINI_API_KEY = "AIzaSyB8ngH9g5xjZt9bLm4O1PbzwuT6CT9zNyI" 

def get_current_time_info():
    """
    Lấy thời gian thực tế hệ thống.
    Output: ('thứ sáu', '16:30')
    """
    now = datetime.now()
    
    # Map số (0=Monday) sang Tiếng Việt lowercase
    days_mapping = {
        0: "thứ hai",
        1: "thứ ba",
        2: "thứ tư",
        3: "thứ năm",
        4: "thứ sáu",
        5: "thứ bảy",
        6: "chủ nhật"
    }
    
    # Lấy thứ và giờ
    current_day = days_mapping[now.weekday()]  # Kết quả: "thứ sáu"
    current_time = now.strftime('%H:%M')       # Kết quả: "11:30"
    
    return "thứ ba", "08:30"

def find_best_restaurants(intent_data, use_cache=False):
    """
    [MAIN FUNCTION]
    Input: intent_data = {'location': '...', 'foods': '...', 'budget': '...'}
    Output: List[Dict] (Danh sách nhà hàng đã lọc)
    """
    print("\n" + "="*50)
    print("🚀 START RESTAURANT SEARCH SERVICE")
    print(f"📥 Input: {intent_data}")
    print("="*50)

    # 1. Chuẩn bị dữ liệu đầu vào
    places = []

# --- [BẮT ĐẦU ĐOẠN SỬA] ---
    # Lấy riêng location và city từ user_intent mới
    loc_part = intent_data.get('location', '').strip()
    city_part = intent_data.get('city', '').strip()

    # Ghép lại thành chuỗi "Location, City" để Geocode hiểu
    # VD: "Quận 1" + "Hồ Chí Minh" -> "Quận 1, Hồ Chí Minh"
    parts = [p for p in [loc_part, city_part] if p]
    raw_location = ", ".join(parts)
    
    foods_list = intent_data.get('foods', [])
    
    # Nối thành chuỗi: "cơm tấm" (để Google search hiểu)
    food_query = " ".join(str(f) for f in foods_list).lower().strip() # Nối chuỗi 
    
    # Chuẩn bị biến cho API
    location_str = raw_location.lower().strip()
    
    
    # 2. Lấy dữ liệu (Từ Cache hoặc API)
    if use_cache:
        print("🧪 MODE: Using Cached Data (output.json)")
        try:
            with open("output.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            places = data.get("local_results", [])
        except FileNotFoundError:
            print("❌ Cache not found. Switching to Live API.")
            use_cache = False # Fallback sang gọi API thật
            
    if not use_cache:
        try:
            # A. Geocode
            lat, lng = geocode_location(location_str, SERP_API_KEY)
            
            # B. Fetch Data
            places = fetch_places_google_maps(food_query, lat, lng, SERP_API_KEY)
            
        except Exception as e:
            print(f"❌ DATA ERROR: {e}")
            return [] # Trả về list rỗng nếu lỗi mạng/API

    if not places:
        print("⚠️ No places found.")
        return []

    # 3. Lọc dữ liệu (Filter Pipeline)
    current_day, current_time = get_current_time_info()
    
    # Nếu muốn hardcode giờ để test thì mở dòng dưới
    # current_day, current_time = "Friday", "00:15"
    
    final_results = filter_and_split_restaurants(
        full_places_data=places,
        location=location_str,
        budget=intent_data.get('budget'),
        foods=food_query,
        current_day=current_day,
        current_time=current_time,
        api_key=GEMINI_API_KEY
    )
    
    # --- [NEW] SẮP XẾP KẾT QUẢ (SORTING) ---
    # Tiêu chí:
    # 1. Rating (cao xuống thấp)
    # 2. Số lượng Review (nhiều xuống ít)
    
# --- [NEW] SẮP XẾP KẾT QUẢ (SORTING) ---
    final_results.sort(
        key=lambda x: (
            x.get('is_currently_open', False), 
            float(x.get('rating', 0) or 0),  
            int(x.get('reviews', 0) or 0)    
        ),
        reverse=True 
    )

# ---------------------------------------------------------
    # 5. CHUẨN HÓA DỮ LIỆU ĐẦU RA (MAPPING DATA)
    # ---------------------------------------------------------
    standardized_output = []

    for r in final_results:
        # [QUAN TRỌNG 1] Lấy object chứa tọa độ thô từ Google (nếu có)
        gps = r.get('gps_coordinates', {})
        
        # Lấy lịch mở cửa
        raw_schedule = r.get('operating_hours', {}) 
        
        # Tạo dictionary mới
        item = {
            "id": r.get("place_id_search") or r.get("place_id") or str(hash(r.get('title'))),
            "name": r.get("title", "Không tên"),
            "address": r.get("address", "Đang cập nhật"),
            "rating": float(r.get("rating", 0) or 0),
            "reviews": int(r.get("reviews", 0) or 0),
            "price": r.get("estimated_price", 0), 
            "is_open": r.get("is_currently_open", False),
            "minutes_left": r.get("minutes_left", 0),
            
            # --- [QUAN TRỌNG 2] BẮT TỌA ĐỘ LAT/LONG TẠI ĐÂY ---
            # Nếu có gps thì lấy latitude/longitude, không thì trả về None
            "lat": gps.get("latitude") if gps else None,
            "lng": gps.get("longitude") if gps else None,
            # --------------------------------------------------
            
            "opening_schedule": raw_schedule, 
            "image": r.get("thumbnail"),
            "link": r.get("links", {}).get("directions") or r.get("link")
        }
        standardized_output.append(item)
    
    # In thông báo và trả về
    print(f"\n✅ SERVICE COMPLETED: Found {len(standardized_output)} restaurants.")
    return standardized_output