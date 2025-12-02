# geo_utils.py
from math import radians, cos, sin, asin, sqrt
from constants import DISTRICT_CENTERS

def geocode_location(location: str):
    location = location.strip()
    if not location:
        raise ValueError("Location không được để trống")
    
    loc_lower = location.lower()
    for key, coord in DISTRICT_CENTERS.items():
        if key.lower() in loc_lower or loc_lower in key.lower():
            return coord
    
    return DISTRICT_CENTERS["District 1"]

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return round(R * c, 3)
