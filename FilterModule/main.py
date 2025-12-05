# main.py
import pandas as pd
from datetime import datetime
from FilterModule.filter_utils import prefilter, postfilter, fallback_expand_search, filter_and_split_restaurants

def app(intent_data, current_time=None, min_results=5):
    """
    Hàm chính để lọc nhà hàng - chỉ trả về kết quả, không hiển thị
    """
    # 1. Load dữ liệu
    try:
        df = pd.read_csv("./FilterModule/food.csv", sep=";")
    except FileNotFoundError:
        print("File 'food.csv' not found!")
        return [], []
    
    # 2. Xử lý current_time
    if current_time is None:
        current_time = datetime.now().strftime("%H:%M")
    
    # 3. Prefilter - Lọc theo location và thời gian mở cửa
    pre = prefilter(df, location=intent_data.get("location"), current_time=current_time)
    if pre.empty:
        return [], []
    
    # 4. Postfilter - Lọc theo taste, budget, foods
    post = postfilter(
        pre,
        taste=intent_data.get("taste"),
        budget=intent_data.get("budget"),
        foods=intent_data.get("foods"),
        original_location=intent_data.get("location")
    )
    
    # 5. Fallback search nếu không đủ kết quả
    if len(post) < min_results:
        post = fallback_expand_search(
            full_df=df,
            original_location=intent_data.get("location"),
            taste=intent_data.get("taste"),
            budget=intent_data.get("budget"),
            foods=intent_data.get("foods"),
            existing_results_df=post,
            min_results=min_results,
            current_time=current_time
        )
    
    # 6. Chia thành 2 danh sách
    main_restaurants, supplementary_restaurants = filter_and_split_restaurants(
        full_df=df,
        location=intent_data.get("location"),
        taste=intent_data.get("taste"),
        budget=intent_data.get("budget"),
        foods=intent_data.get("foods"),
        current_time=current_time,
        min_results=min_results
    )
    
    # 7. Trả về 2 danh sách
    return main_restaurants, supplementary_restaurants
