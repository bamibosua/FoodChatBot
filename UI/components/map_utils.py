import time         
import requests     
import folium        
import os            
import polyline      

from Translator.translator import translate_text
from Utils.key_manager import get_serp_key
from FilterModule.data_utils import geocode_location
SERP_API_KEY = get_serp_key()

# Nominatim (OpenStreetMap)
# Dùng để chuyển địa chỉ (text) -> tọa độ (latitude, longitude)
NOMINATIM = "https://nominatim.openstreetmap.org"

# OpenRouteService
# API chính để tính toán đường đi (routing) bằng xe hơi
ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

# API key của ORS
# Ưu tiên lấy từ biến môi trường, nếu không có thì dùng key mặc định
ORS_KEY = os.getenv(
    "ORS_KEY",
    "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6Ijc0NTJjMTMyNWEzMjQwMDI5ZDAxMTViOGJjZjg5YTU2IiwiaCI6Im11cm11cjY0In0="
)

# OSRM public server
# Dùng làm phương án dự phòng khi ORS bị lỗi
OSRM = "https://router.project-osrm.org"

# User-Agent
UA = {
    "User-Agent": "FoodApp/1.0 (contact: huynhthiyenvy588@gmail.com)"
}

def geocode(q):
    """
    Chuyển địa chỉ dạng text thành tọa độ (lat, lon)

    Parameters:
        q (str): địa chỉ cần tìm

    Returns:
        lat (float): vĩ độ
        lon (float): kinh độ
        display_name (str): tên đầy đủ của địa chỉ
    """

    # Sleep 1 giây để tránh spam API Nominatim
    time.sleep(1.0)

    translated = translate_text(q, 'vi')
    search_lat, search_lng = geocode_location(translated, SERP_API_KEY)

    # Trả về lat, lon và tên hiển thị của địa chỉ
    return (
        float(search_lat),
        float(search_lng),
        translated
    )


def osrm_geom(lon1, lat1, lon2, lat2):
    """
    Hàm routing tổng
    Ưu tiên dùng OpenRouteService
    Nếu ORS lỗi thì fallback sang OSRM
    """

    try:
        # Thử routing bằng ORS trước
        return ors_routing(lon1, lat1, lon2, lat2)
    except Exception as e:
        # Nếu ORS fail thì log lỗi và dùng OSRM
        print(f"⚠️ ORS failed ({str(e)}), trying OSRM...")
        return osrm_routing(lon1, lat1, lon2, lat2)


def ors_routing(lon1, lat1, lon2, lat2):
    """
    Routing bằng OpenRouteService
    ORS trả về geometry dưới dạng encoded polyline (STRING)
    Cần decode và convert sang GeoJSON
    """

    # Header cho ORS
    headers = {
        "Authorization": ORS_KEY,
        "Content-Type": "application/json"
    }

    # Body request
    # ORS sử dụng format [lon, lat]
    body = {
        "coordinates": [
            [lon1, lat1],
            [lon2, lat2]
        ]
    }

    # Gửi POST request tới ORS
    r = requests.post(
        ORS_URL,
        json=body,
        headers=headers,
        timeout=15
    )

    # Nếu request lỗi -> raise exception
    r.raise_for_status()

    # Parse JSON response
    data = r.json()

    # Kiểm tra có route hay không
    if "routes" not in data or len(data["routes"]) == 0:
        raise Exception("No routes found")

    # Lấy route đầu tiên
    route = data["routes"][0]
    summary = route["summary"]

    # Geometry của ORS là encoded polyline (chuỗi)
    encoded_polyline = route["geometry"]

    # Decode polyline -> danh sách (lat, lon)
    decoded_coords = polyline.decode(encoded_polyline)

    # Convert sang GeoJSON LineString
    # GeoJSON yêu cầu format (lon, lat)
    geometry = {
        "type": "LineString",
        "coordinates": [[lon, lat] for lat, lon in decoded_coords]
    }

    # Khoảng cách (m -> km)
    distance_km = summary["distance"] / 1000.0

    # Thời gian (s -> giờ)
    duration_hrs = summary["duration"] / 3600.0

    # Trả về geometry + distance + duration
    return geometry, distance_km, duration_hrs



def osrm_routing(lon1, lat1, lon2, lat2):
    """
    Routing bằng OSRM (fallback)
    OSRM trả về geometry sẵn ở dạng GeoJSON
    """

    # Gửi GET request tới OSRM
    r = requests.get(
        f"{OSRM}/route/v1/driving/{lon1},{lat1};{lon2},{lat2}",
        params={
            "overview": "full",     # Lấy full geometry
            "geometries": "geojson" # Format GeoJSON
        },
        headers=UA,
        timeout=20
    )

    # Nếu request lỗi -> raise exception
    r.raise_for_status()

    # Parse JSON response
    data = r.json()

    # Kiểm tra trạng thái
    if data.get("code") != "Ok":
        raise Exception(f"OSRM error: {data.get('message', 'Unknown')}")

    # Lấy route đầu tiên
    route = data["routes"][0]

    # Trả về geometry + distance + duration
    return (
        route["geometry"],
        route["distance"] / 1000.0,  # m -> km
        route["duration"] / 3600.0   # s -> giờ
    )

def create_multi_destination_map(start, destinations):
    """
    Tạo bản đồ Folium với:
    - 1 điểm bắt đầu
    - Nhiều điểm đến
    - Mỗi tuyến đường là 1 layer riêng

    Parameters:
        start (str): địa chỉ điểm bắt đầu
        destinations (list): danh sách điểm đến (lat, lng, name...)

    Returns:
        folium.Map
        route_info (dict)
    """

    try:
        # Geocode điểm bắt đầu
        lat_start, lon_start, name_start = geocode(start)

        # Tạo map với tâm là điểm start
        m = folium.Map(location=[lat_start, lon_start], zoom_start=14)

        # Marker cho điểm bắt đầu
        folium.Marker(
            [lat_start, lon_start],
            popup=f"<b>Start:</b><br>{name_start}",
            tooltip="Starting Point",
            icon=folium.Icon(color='green', icon='home', prefix='fa')
        ).add_to(m)

        # Danh sách màu cho các route
        colors = [
            'blue', 'red', 'purple', 'orange',
            'darkred', 'cadetblue', 'darkgreen', 'pink'
        ]

        # Lưu thông tin route để trả về backend
        route_info = {}

        # Loop qua từng điểm đến
        for idx, dest in enumerate(destinations):
            try:
                # Nếu thiếu tọa độ thì bỏ qua
                if not dest.get("lat") or not dest.get("lng"):
                    continue

                lat_dest = dest["lat"]
                lon_dest = dest["lng"]
                name_dest = dest.get("name", f"Destination {idx+1}")

                # Tính route từ start -> destination
                geom, km, hrs = osrm_geom(
                    lon_start, lat_start,
                    lon_dest, lat_dest
                )

                # Chọn màu cho route
                color = colors[idx % len(colors)]

                # Mỗi route là một FeatureGroup (layer)
                fg = folium.FeatureGroup(
                    name=f"{name_dest} ({km:.1f} km)",
                    show=True
                )

                # Marker cho điểm đến
                folium.Marker(
                    [lat_dest, lon_dest],
                    popup=f"<b>{name_dest}</b><br>{km:.1f} km, {hrs*60:.0f} min",
                    tooltip=name_dest,
                    icon=folium.Icon(color=color, icon='utensils', prefix='fa')
                ).add_to(fg)

                # GeoJSON dùng (lon, lat)
                # Folium cần (lat, lon) -> phải đảo lại
                latlon = [(lat, lon) for lon, lat in geom["coordinates"]]

                # Vẽ polyline (đường đi)
                folium.PolyLine(
                    latlon,
                    weight=4,
                    color=color,
                    opacity=0.7,
                    popup=f"{name_dest}: {km:.1f} km"
                ).add_to(fg)

                # Thêm layer vào map
                fg.add_to(m)

                # Lưu thông tin route
                route_info[name_dest] = {
                    'distance_km': km,
                    'duration_hrs': hrs,
                    'color': color,
                    'address': dest.get("address", "N/A")
                }

            except Exception as e:
                # Nếu route của điểm nào lỗi thì vẫn tiếp tục điểm khác
                route_info[name_dest] = {'error': str(e)}

        # Control bật/tắt các layer
        folium.LayerControl(collapsed=True).add_to(m)

        # Trả về map và info
        return m, route_info

    except Exception as e:
        # Lỗi tổng (ví dụ geocode start fail)
        return None, {'error': str(e)}