# components/map_utils.py
import time
import requests
import folium

NOMINATIM = "https://nominatim.openstreetmap.org"
OSRM = "https://router.project-osrm.org"
UA = {"User-Agent": "OSM-Demo-Folium/1.0 (contact: huynhvy180706@gmail.com)"}

def geocode(q):
    """Lấy tọa độ từ địa chỉ"""
    time.sleep(1.0)
    r = requests.get(
        f"{NOMINATIM}/search",
        params={"q": q, "format": "jsonv2", "limit": 1,"accept-language": "en"},
        headers=UA
    )
    r.raise_for_status()
    j = r.json()
    if not j:
        raise ValueError(f"Không tìm thấy: {q}")
    return float(j[0]["lat"]), float(j[0]["lon"]), j[0].get("display_name", q)

def osrm_geom(lon1, lat1, lon2, lat2):
    """Lấy tuyến đường từ OSRM"""
    r = requests.get(
        f"{OSRM}/route/v1/driving/{lon1},{lat1};{lon2},{lat2}",
        params={"overview":"full","geometries":"geojson"},
        headers=UA, timeout=120
    )
    r.raise_for_status()
    data = r.json()
    route = data["routes"][0]
    return route["geometry"], route["distance"]/1000.0, route["duration"]/3600.0

def create_route_map(start, end):
    try:
        lat1, lon1, n1 = geocode(start)
        lat2, lon2, n2 = geocode(end)
        geom, km, hrs = osrm_geom(lon1, lat1, lon2, lat2)

        # Map trung điểm
        m = folium.Map(location=[(lat1+lat2)/2, (lon1+lon2)/2], zoom_start=5)
        folium.Marker([lat1, lon1], popup=n1).add_to(m)
        folium.Marker([lat2, lon2], popup=n2).add_to(m)

        # Vẽ tuyến đường
        latlon = [(lat, lon) for lon, lat in geom["coordinates"]]
        folium.PolyLine(latlon, weight=5, color="blue").add_to(m)

        info = f"Tuyến: ~{km:,.1f} km, ~{hrs:,.1f} giờ"
        return m, info
    except Exception as e:
        return None, str(e)
