# filter_utils.py
import pandas as pd
import re
from datetime import datetime
from geo_utils import geocode_location, haversine
from time_utils import is_open
from price_utils import parse_price

def prefilter(df, location=None, current_time=None):
    if current_time is None:
        current_time = datetime.now().strftime("%H:%M")
    df = df.copy()
    
    filtered_rows = []
    if location and location.strip():
        location_clean = location.strip().lower()
        for _, row in df.iterrows():
            district_clean = str(row['district']).strip().lower()
            if district_clean == location_clean:
                filtered_rows.append(row.to_dict())
    else:
        filtered_rows = df.to_dict('records')
    
    if not filtered_rows:
        return pd.DataFrame()
    
    df_filtered = pd.DataFrame(filtered_rows)
    
    open_status = df_filtered["open_hours"].apply(lambda t: is_open(t, current_time))
    df_filtered["is_open"] = [x[0] for x in open_status]
    df_filtered["minutes_left"] = [x[1] for x in open_status]
    df_filtered = df_filtered[(df_filtered["is_open"]) & (df_filtered["minutes_left"] >= 30)]
    
    return df_filtered

def postfilter(df, taste=None, budget=None, foods=None, original_location=None, is_fallback=False):
    if df.empty:
        return pd.DataFrame()

    filtered_data = []
    
    required_tags = set()
    required_foods = None
    has_taste = False
    has_foods = False

    if taste is not None and taste != "None" and taste != "none":
        if isinstance(taste, str):
            clean = taste.strip()
            if clean and clean.lower() != "none":
                required_tags = {t.strip().lower() for t in clean.split(",") if t.strip() and t.strip().lower() != "none"}
        elif isinstance(taste, list):
            required_tags = {str(t).strip().lower() for t in taste if t and str(t).strip().lower() != "none"}
        has_taste = bool(required_tags)

    if foods is not None and foods != "None" and foods != "none":
        if isinstance(foods, str):
            clean = str(foods).strip()
            if clean and clean.lower() != "none":
                required_foods = [clean.lower()]
                has_foods = True
        elif isinstance(foods, list):
            cleaned_list = [str(f).strip().lower() for f in foods 
                          if f and str(f).strip().lower() != "none"]
            if cleaned_list:
                required_foods = cleaned_list
                has_foods = True

    parsed_budget = parse_price(budget)

    print(f"\n[POSTFILTER DEBUG]")
    print(f"  has_taste: {has_taste} | tags: {required_tags if has_taste else 'N/A'}")
    print(f"  has_foods: {has_foods} | food: {required_foods if has_foods else 'N/A'}")
    print(f"  budget: {parsed_budget if parsed_budget else 'N/A'}")
    print(f"  Mode: ", end="")
    if has_foods and has_taste:
        print("BOTH foods + taste")
    elif has_foods:
        print("ONLY foods (ignore taste)")
    elif has_taste:
        print("ONLY taste (ignore foods)")
    else:
        print("NO filter (keep all, check budget only)")
    print()

    if original_location and not is_fallback:
        try:
            root_lat, root_lon = geocode_location(original_location)
            dists = []
            for _, row in df.iterrows():
                try:
                    lat, lon = map(float, str(row["coordinates"]).split(","))
                    d = haversine(root_lat, root_lon, lat, lon)
                    dists.append(d)
                except:
                    dists.append(float("inf"))
            df["distance_km"] = dists
        except:
            df["distance_km"] = float("inf")

    for _, row in df.iterrows():
        match_score = 1.0 if not is_fallback else 0.5
        
        taste_match = False
        taste_score = 0
        if has_taste:
            row_tags = str(row.get("taste_tags", "")).lower().strip()
            row_set = {t.strip() for t in row_tags.split(",") if t.strip()}
            match_count = len(required_tags.intersection(row_set))
            if match_count > 0:
                taste_match = True
                taste_score = match_count * 0.15

        foods_match = False
        foods_score = 0
        if has_foods:
            food_tag = str(row.get("food_tags", "")).strip().lower()
            
            match_all = True
            for food_keyword in required_foods:
                if not re.search(rf'\b{re.escape(food_keyword)}\b', food_tag):
                    match_all = False
                    break
            
            if match_all:
                foods_match = True
                foods_score = 0.5

        if has_foods and has_taste:
            if foods_match and taste_match:
                match_score += foods_score + taste_score
            elif foods_match:
                match_score += foods_score
            elif taste_match:
                match_score += taste_score * 0.5
            else:
                if not is_fallback:
                    continue
                match_score = min(match_score, 0.4)
                
        elif has_foods:
            if not foods_match:
                if not is_fallback:
                    continue
                match_score = min(match_score, 0.5)
            else:
                match_score += foods_score
                
        elif has_taste:
            if not taste_match:
                if not is_fallback:
                    continue
                match_score = min(match_score, 0.5)
            else:
                match_score += taste_score

        if parsed_budget is not None:
            min_price = parse_price(str(row.get("budget", "")))
            if min_price is not None:
                if min_price > parsed_budget:
                    if not is_fallback:
                        continue
                    else:
                        match_score = min(match_score, 0.5)

        match_score = min(match_score, 1.5)
        
        row_dict = row.to_dict()
        row_dict["match_score"] = match_score
        filtered_data.append(row_dict)

    filtered = pd.DataFrame(filtered_data)
    if filtered.empty:
        return filtered

    if "distance_km" in filtered.columns:
        filtered = filtered.sort_values(["match_score", "distance_km"], ascending=[False, True])
    else:
        filtered = filtered.sort_values("match_score", ascending=False)

    return filtered

def fallback_expand_search(full_df, original_location, taste=None, budget=None, foods=None,
                           existing_results_df=None, min_results=5, current_time=None):

    if existing_results_df is None:
        existing_results_df = pd.DataFrame()

    current_count = len(existing_results_df)
    if current_count >= min_results:
        return existing_results_df

    need = min_results - current_count

    try:
        root_lat, root_lon = geocode_location(original_location)
    except:
        return existing_results_df

    df_open = full_df.copy()
    open_status = df_open["open_hours"].apply(lambda t: is_open(t, current_time))
    df_open["is_open"] = [x[0] for x in open_status]
    df_open["minutes_left"] = [x[1] for x in open_status]
    df_open = df_open[(df_open["is_open"]) & (df_open["minutes_left"] >= 30)]

    if df_open.empty:
        return existing_results_df

    if not existing_results_df.empty:
        used = set(existing_results_df["id"])
        df_open = df_open[~df_open["id"].isin(used)]

    if df_open.empty:
        return existing_results_df

    candidates = df_open.copy()
    
    required_foods = None
    has_foods = False
    
    if foods is not None and foods != "None" and foods != "none":
        if isinstance(foods, str):
            clean = str(foods).strip()
            if clean and clean.lower() != "none":
                required_foods = [clean.lower()]
                has_foods = True
        elif isinstance(foods, list):
            cleaned_list = [str(f).strip().lower() for f in foods 
                          if f and str(f).strip().lower() != "none"]
            if cleaned_list:
                required_foods = cleaned_list
                has_foods = True

    candidates = df_open.copy()
    
    if has_foods and required_foods:
        food_matches = []
        for _, row in candidates.iterrows():
            food_tag = str(row.get("food_tags", "")).strip().lower()
            
            match_all = True
            for food_keyword in required_foods:
                if not re.search(rf'\b{re.escape(food_keyword)}\b', food_tag):
                    match_all = False
                    break
            
            food_matches.append(match_all)
        
        candidates = candidates[food_matches]

    parsed_budget = parse_price(budget)

    def compute_dist(coord_str):
        try:
            lat, lon = map(float, coord_str.split(","))
            return haversine(root_lat, root_lon, lat, lon)
        except:
            return float("inf")

    candidates["distance_km"] = candidates["coordinates"].apply(compute_dist)
    candidates["match_score"] = 0.5

    candidates["rating"] = pd.to_numeric(candidates["rating"], errors="coerce")
    candidates = candidates.sort_values(
        ["rating", "distance_km"],
        ascending=[False, True]
    )

    to_add = candidates.head(need).copy()

    final = pd.concat([existing_results_df, to_add], ignore_index=True)
    return final

def filter_and_split_restaurants(full_df, location, taste=None, budget=None, 
                                 foods=None, current_time=None, min_results=5):
    if current_time is None:
        current_time = datetime.now().strftime("%H:%M")
    
    main_results = prefilter(full_df, location=location, current_time=current_time)
    main_results = postfilter(
        main_results,
        taste=taste,
        budget=budget,
        foods=foods,
        original_location=location,
        is_fallback=False
    )
    
    if not main_results.empty:
        main_results["rating"] = pd.to_numeric(main_results["rating"], errors="coerce")
        main_results = main_results.sort_values(
            ["match_score", "rating", "distance_km"],
            ascending=[False, False, True]
        )

    main_count = len(main_results)
    
    if main_count >= min_results:
        main_list = main_results.head(min_results).to_dict('records')
        supplementary_list = []
        return main_list, supplementary_list
    
    final_results = fallback_expand_search(
        full_df=full_df,
        original_location=location,
        taste=taste,
        budget=budget,
        foods=foods,
        existing_results_df=main_results,
        min_results=min_results,
        current_time=current_time
    )

    if not final_results.empty:
        final_results["rating"] = pd.to_numeric(final_results["rating"], errors="coerce")
        final_results = final_results.sort_values(
            ["match_score", "rating", "distance_km"],
            ascending=[False, False, True]
        )
    
    main_list = main_results.to_dict('records')
    
    if len(final_results) > main_count:
        supplementary_results = final_results.iloc[main_count:]
        supplementary_list = supplementary_results.to_dict('records')
    else:
        supplementary_list = []
    
    return main_list, supplementary_list
