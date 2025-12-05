def isInHCM(city: str):
    city_norm = city.strip().lower()

    hcm_aliases = [
        "ho chi minh",
        "ho chi minh city",
        "hcm",
        "sai gon",
        "saigon",
    ]

    if city_norm in hcm_aliases:
        return True
    else:
        return False