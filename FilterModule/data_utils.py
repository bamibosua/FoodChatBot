import json
import time
import math
import requests
from serpapi.google_search import GoogleSearch

# --- CẤU HÌNH CƠ BẢN ---
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
UA = {"User-Agent": "FoodApp_StudentProject/1.0"}

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Tính khoảng cách giữa 2 điểm GPS (đơn vị: km) dùng công thức Haversine.
    """
    if not lat1 or not lon1 or not lat2 or not lon2:
        return 9999.0 # Nếu thiếu tọa độ, coi như rất xa
        
    R = 6371.0 # Bán kính trái đất (km)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance
# ------------------------------------------------------------
# 1) Geocode Fallback (OSM)
# ------------------------------------------------------------
def geocode_osm_fallback(query):
    """
    Tìm tọa độ bằng OpenStreetMap nếu Google (SerpApi) bị lỗi.
    """
    print(f"   🚑 [Fallback] Đang chuyển sang OpenStreetMap tìm: '{query}'...")
    try:
        if "việt nam" not in query.lower():
            query += ", Việt Nam"
            
        time.sleep(1) # Delay 1s để tránh bị chặn
        resp = requests.get(NOMINATIM_URL, params={
            "q": query, "format": "jsonv2", "limit": 1
        }, headers=UA, timeout=10)
        
        data = resp.json()
        if data:
            item = data[0]
            lat, lng = float(item['lat']), float(item['lon'])
            print(f"   ✅ [Source: OSM Fallback] Tọa độ: {lat}, {lng}")
            return lat, lng
        else:
            print(f"   ⚠️ OSM cũng không tìm thấy địa điểm này.")
    except Exception as e:
        print(f"   ⚠️ Lỗi kết nối OSM: {e}")
    return None, None

# ------------------------------------------------------------
# 2) Geocode Chính (SerpApi -> Lỗi thì sang OSM)
# ------------------------------------------------------------
def geocode_location(text_location: str, api_key: str):
    """
    Chuyển tên địa điểm thành tọa độ (lat, lng) sử dụng SerpApi, với OSM là Fallback.
    """
    print(f"🌍 Geocoding (SerpApi): '{text_location}'...")
    
    params = {
        "engine": "google_maps",
        "type": "search", 
        "q": text_location,
        "api_key": api_key,
        "google_domain": "google.com.vn",
        "gl": "vn",
        "hl": "vi"
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        # --- KIỂM TRA LỖI API GOOGLE ---
        if "error" in results:
            print(f"   ❌ SERPAPI ERROR: {results['error']}")
            # Lỗi Google -> Gọi ngay OSM
            lat, lng = geocode_osm_fallback(text_location)
            if lat and lng: return lat, lng
            raise Exception(f"Google lỗi và OSM cũng không tìm thấy '{text_location}'")

        lat, lng = None, None

        # Chiến thuật tìm kiếm tọa độ trong kết quả của SerpApi
        fallback_sources = [
            ("place_results", "gps_coordinates"),
            ("local_results", lambda x: x[0].get("gps_coordinates") if x else None),
            ("search_results", lambda x: x[0].get("gps_coordinates") if x else None),
        ]

        for source, extractor in fallback_sources:
            if lat and lng: break
            data = results.get(source)
            if not data: continue

            try:
                gps = extractor(data) if callable(extractor) else data.get(extractor)
                if gps:
                    lat, lng = gps.get('latitude'), gps.get('longitude')
                    if lat and lng:
                        print(f"   ✅ [Source: {source}] Tọa độ: {lat}, {lng}")
            except: continue

        # Nếu tìm thấy thì trả về
        if lat and lng:
            return float(lat), float(lng)
            
        # Nếu SerpApi trả về rỗng (không lỗi nhưng không có lat/lng) -> Gọi OSM
        print(f"   ⚠️ Google không có dữ liệu tọa độ. Gọi OSM...")
        lat, lng = geocode_osm_fallback(text_location)
        
        if lat and lng:
            return lat, lng

        raise Exception(f"Không tìm thấy tọa độ cho '{text_location}'")

    except Exception as e:
        print(f"❌ Geocode Error: {e}")
        # Lớp bảo vệ cuối cùng: Nếu Code crash, thử gọi OSM lần cuối
        lat, lng = geocode_osm_fallback(text_location)
        if lat and lng: return lat, lng
        raise

# ------------------------------------------------------------
# 3) Fetch local places từ Google Maps engine
# ------------------------------------------------------------
def fetch_places_google_maps(query: str, lat: float, lng: float, api_key: str, 
                             output_file="output.json"):
    """
    Tìm kiếm địa điểm quanh tọa độ GPS với cơ chế thử nhiều mức Zoom.
    """
    # Các mức zoom để thử: 15 (Gần) -> 10 (Rất xa)
    zoom_levels = [15, 13, 12, 11, 10]
    
    for zoom in zoom_levels:
        print(f"📡 SerpApi Searching: '{query}' @ [{lat}, {lng}] (Zoom {zoom}z)...")
        
        params = {
            "engine": "google_maps",
            "type": "search",
            "q": query,
            "ll": f"@{lat},{lng},{zoom}z", 
            "google_domain": "google.com.vn",
            "gl": "vn",
            "hl": "vi",
            "api_key": api_key,
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()

            # Check lỗi API
            if "error" in results:
                print(f"   ⚠️ Lỗi Zoom {zoom}z: {results['error']}")
                time.sleep(1) # Nghỉ 1 chút rồi thử zoom khác
                continue 

            local_results = results.get("local_results", [])
            
            if local_results:
                print(f"   ✅ Tìm thấy {len(local_results)} địa điểm ở Zoom {zoom}z.")
                
                # Lưu file debug cho lần thành công
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=4)
                    
                return local_results
            else:
                print(f"   ⚠️ Không tìm thấy quán ở Zoom {zoom}z. Thử mở rộng phạm vi...")
        
        except Exception as e:
            print(f"   ❌ Lỗi kết nối ở Zoom {zoom}z: {e}")
            
    print("❌ Đã thử mọi mức Zoom nhưng không tìm thấy quán nào.")
    return []

