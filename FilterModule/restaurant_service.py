# FilterModule/restaurant_service.py
import json
import os
from datetime import datetime
from .data_utils import geocode_location, fetch_places_google_maps, calculate_distance
from .filter_utils import filter_and_split_restaurants
from Utils.key_manager import get_keys, get_serp_key 

# Lấy SerpApi Key từ Key Manager
SERP_API_KEY = get_serp_key()

def get_current_time_info():
    """Lấy ngày và giờ hiện tại."""
    now = datetime.now()
    days_mapping = {0: "thứ hai", 1: "thứ ba", 2: "thứ tư", 3: "thứ năm", 4: "thứ sáu", 5: "thứ bảy", 6: "chủ nhật"}
    current_day = days_mapping[now.weekday()]
    current_time = now.strftime('%H:%M')
    return "thứ ba", "08:30"

def find_best_restaurants(intent_data, use_cache=False):
    """
    Chạy toàn bộ quy trình tìm kiếm, lọc và sắp xếp nhà hàng (Có tính khoảng cách).
    """
    print("\n" + "="*50)
    print("🚀 START RESTAURANT SEARCH SERVICE")
    print(f"📥 Input: {intent_data}")
    print("="*50)

    # 1. Chuẩn bị dữ liệu đầu vào
    places = []
    
    # Lấy location trọn vẹn (VD: "Quận 1, Hồ Chí Minh")
    raw_location = intent_data.get('location', '').strip()
    
    foods_list = intent_data.get('foods', [])
    food_query = " ".join(str(f) for f in foods_list).lower().strip()
    location_str = raw_location.lower().strip()
    
    # Biến lưu tọa độ tâm tìm kiếm
    search_lat, search_lng = None, None

    # 2. Lấy dữ liệu (Từ Cache hoặc Live API)
    if use_cache:
        print("🧪 MODE: Using Cached Data (output.json)")
        try:
            with open("output.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            places = data.get("local_results", [])
            # Nếu dùng cache, thử fake tọa độ tâm để test logic sort (hoặc để None)
            search_lat, search_lng = 10.7769, 106.7009 # VD: Tọa độ Q1
        except FileNotFoundError:
            print("❌ Cache not found. Switching to Live API.")
            use_cache = False 
            
    if not use_cache:
        try:
            # A. Geocode để lấy tọa độ TÂM TÌM KIẾM
            search_lat, search_lng = geocode_location(location_str, SERP_API_KEY) 
            
            # B. Fetch Places xung quanh tâm đó
            places = fetch_places_google_maps(food_query, search_lat, search_lng, SERP_API_KEY)
        except Exception as e:
            print(f"❌ DATA ERROR: {e}")
            return []

    if not places:
        print("⚠️ No places found.")
        return []

    # 3. Lọc dữ liệu (Filter Pipeline)
    current_day, current_time = get_current_time_info()
    
    final_results = filter_and_split_restaurants(
        full_places_data=places,
        location=location_str,
        budget=intent_data.get('budget'),
        foods=food_query,
        current_day=current_day,
        current_time=current_time
    )
    
    # 4. TÍNH KHOẢNG CÁCH & SẮP XẾP
    # -----------------------------------------------------------
    # Bước 4a: Tính khoảng cách từ tâm tìm kiếm đến từng quán
    for r in final_results:
        gps = r.get('gps_coordinates', {})
        r_lat = gps.get('latitude')
        r_lng = gps.get('longitude')
        
        if search_lat and search_lng and r_lat and r_lng:
            dist = calculate_distance(search_lat, search_lng, r_lat, r_lng)
        else:
            dist = 99.9 # Nếu không tính được thì coi như xa
            
        r['distance_km'] = dist

    
    # Bước 4b: Sắp xếp
    final_results.sort(
        key=lambda x: (
            # Ưu tiên 1: Đang mở cửa (True > False)
            x.get('is_currently_open', False), 
            
            # Ưu tiên 2: Khoảng cách GẦN NHẤT
            # (Dùng số âm của distance vì reverse=True: -0.5 > -10)
            -x.get('distance_km', 9999),
            
            # Ưu tiên 3: Rating cao
            float(x.get('rating', 0) or 0),  
            
            # Ưu tiên 4: Review nhiều
            int(x.get('reviews', 0) or 0)    
        ),
        reverse=True # Sắp xếp giảm dần
    )

    # =======================================================
    # [FIX] GIỚI HẠN LẤY 5 KẾT QUẢ TỐT NHẤT
    # =======================================================
    final_results = final_results[:5]
    # =======================================================
    
    # 5. Chuẩn hóa Output
    standardized_output = []
    for r in final_results:
        gps = r.get('gps_coordinates', {})
        raw_schedule = r.get('operating_hours', {}) 
        
        item = {
            "id": r.get("place_id_search") or r.get("place_id") or str(hash(r.get('title'))),
            "name": r.get("title", "Không tên"),
            "address": r.get("address", "Đang cập nhật"),
            "rating": float(r.get("rating", 0) or 0),
            "reviews": int(r.get("reviews", 0) or 0),
            "price": r.get("estimated_price", 0), 
            "is_open": r.get("is_currently_open", False), 
            "minutes_left": r.get("minutes_left", 0), 
            "lat": gps.get("latitude") if gps else None,
            "lng": gps.get("longitude") if gps else None,
            
            # [MỚI] Thêm khoảng cách vào output
            "distance": round(r.get('distance_km', 0), 2),
            
            "opening_schedule": raw_schedule, 
            "image": r.get("thumbnail"),
            "link": r.get("links", {}).get("directions") or r.get("link")
        }
        standardized_output.append(item)
    
    print(f"\n✅ SERVICE COMPLETED: Found {len(standardized_output)} restaurants.")
    return standardized_output