import json
import time
import requests
from serpapi.google_search import GoogleSearch

# --- CẤU HÌNH OSM (PHAO CỨU SINH MIỄN PHÍ) ---
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
UA = {"User-Agent": "FoodApp_StudentProject/1.0"}

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
# 1) Geocode: SerpApi -> Lỗi thì sang OSM
# ------------------------------------------------------------
def geocode_location(text_location: str, api_key: str):
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

        # # Debug
        # with open("debug_geocode.json", "w", encoding="utf-8") as f:
        #     json.dump(results, f, ensure_ascii=False, indent=4)

        # --- KIỂM TRA LỖI API GOOGLE ---
        if "error" in results:
            print(f"   ❌ SERPAPI ERROR: {results['error']}")
            # Lỗi Google -> Gọi ngay OSM
            lat, lng = geocode_osm_fallback(text_location)
            if lat and lng: return lat, lng
            raise Exception(f"Google lỗi và OSM cũng không tìm thấy '{text_location}'")

        lat, lng = None, None

        # Chiến thuật tìm kiếm của SerpApi
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
# 2) Fetch local places từ Google Maps engine
# ------------------------------------------------------------
def fetch_places_google_maps(query: str, lat: float, lng: float, api_key: str, 
                             output_file="output.json"):
    """
    Tìm kiếm địa điểm quanh tọa độ GPS.
    Có cơ chế thử nhiều mức Zoom để tránh lỗi "No results" ở vùng quê.
    """
    # Các mức zoom để thử: 15 (Gần), 13 (Vừa), 12 (Xa)
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