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

def create_multi_destination_map(start, destinations):
    """
    Map với nhiều điểm đến cố định (giữ lại cho trường hợp dùng địa chỉ có sẵn)
    """
    try:
        lat_start, lon_start, name_start = geocode(start)
        m = folium.Map(location=[lat_start, lon_start], zoom_start=13)
        
        folium.Marker(
            [lat_start, lon_start], 
            popup=f"<b>Start:</b><br>{name_start}",
            tooltip="Starting Point",
            icon=folium.Icon(color='green', icon='home', prefix='fa')
        ).add_to(m)
        
        colors = ['blue', 'red', 'purple', 'orange', 'darkred', 'cadetblue', 'darkgreen', 'pink', 'gray', 'black']
        route_info = {}
        
        for idx, dest in enumerate(destinations):
            try:
                if dest.get("lat") is None or dest.get("lng") is None:
                    continue
                
                lat_dest = dest["lat"]
                lon_dest = dest["lng"]
                name_dest = dest.get("name")
                
                geom, km, hrs = osrm_geom(lon_start, lat_start, lon_dest, lat_dest)
                color = colors[idx % len(colors)]
                
                folium.Marker(
                    [lat_dest, lon_dest],
                    popup=f"<b>{name_dest} {idx+1}:</b><br>{name_dest}<br>{km:.1f} km, {hrs:.1f} hours",
                    tooltip=name_dest,
                    icon=folium.Icon(color=color, icon='utensils', prefix='fa')
                ).add_to(m)
                
                latlon = [(lat, lon) for lon, lat in geom["coordinates"]]
                folium.PolyLine(latlon, weight=4, color=color, opacity=0.7, popup=f"{name_dest}: {km:.1f} km").add_to(m)
                
                route_info[name_dest] = {'distance_km': km, 'duration_hrs': hrs, 'color': color, 'address': dest["address"]}
                
            except Exception as e:
                route_info[name_dest] = {'error': str(e)}
        
        return m, route_info
        
    except Exception as e:
        return None, {'error': str(e)}

#map_utils.py