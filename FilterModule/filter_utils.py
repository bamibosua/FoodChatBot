# filter_utils.py
import json
from groq import Groq
from .time_utils import filter_open_restaurants
from .price_utils import parse_price, parse_price_range
from Utils.key_manager import get_keys, get_model_name 

MODEL_NAME = get_model_name()

# ------------------------------------------------------------------
# 1. HÀM AI LỌC MÓN ĂN
# ------------------------------------------------------------------
def ai_check_food_relevance_batch(restaurants, food_query):
    """Lọc danh sách nhà hàng theo món ăn bằng AI (Gọi trực tiếp)."""
    if not food_query or not restaurants: 
        return restaurants

    # Rút gọn data gửi AI
    input_list = [{'id': i, 'n': r.get('title', ''), 't': r.get('types', [])} 
                  for i, r in enumerate(restaurants)]
    
    print(f"🤖 [GROQ] Check '{food_query}' ({len(restaurants)} quán)...")

    prompt = f"""
    Lọc danh sách quán khớp với món: "{food_query}".
    DATA: {json.dumps(input_list, ensure_ascii=False)}
    OUTPUT JSON ONLY format: {{"ids": [list_of_valid_ids]}}
    """
    
    try:
        keys = get_keys()
        if not keys:
            print("   ❌ Lỗi: Không có API Key.")
            return restaurants

        # Gọi trực tiếp Groq tại đây
        client = Groq(api_key=keys[0])
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that outputs valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=MODEL_NAME,
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        result_text = chat_completion.choices[0].message.content
        result_json = json.loads(result_text)
        valid_indices = result_json.get('ids', [])
        
        filtered = [restaurants[i] for i in valid_indices if i < len(restaurants)]
        print(f"   ⚡ AI chốt: {len(filtered)}/{len(restaurants)} quán.")
        return filtered

    except Exception as e:
        print(f"   ⚠️ Lỗi AI hoặc parse JSON: {e}")
        return restaurants

# ------------------------------------------------------------------
# 2. PRE-FILTER (Lọc Địa điểm, Thời gian, Món ăn)
# ------------------------------------------------------------------
def prefilter(local_results, location=None, foods=None, current_day=None, current_time=None):
    """
    Pipeline lọc dữ liệu (Bỏ qua Location -> Time -> Food).
    """
    print(f"\n🔍 PIPELINE START (Input: {len(local_results)} quán)")
    current_results = local_results

    # ===== STEP 1: LOCATION FILTER (ĐÃ VÔ HIỆU HÓA) =====
    # Logic cũ đã được bỏ qua để giữ lại toàn bộ kết quả từ Google Maps
    if location:
        print(f"📍 [STEP 1] Location Filter: '{location}'")
        print(f"   ⏩ ĐÃ TẮT LỌC LOCATION (Giữ nguyên {len(current_results)} quán từ Google Maps).")
    else:
        print("⏩ Bỏ qua Location (Không có input).")

    # ===== STEP 2: TIME FILTER (Kiểm tra trạng thái mở cửa) =====
    if current_results:
        print(f"⏰ [STEP 2] Time Filter (Check: {current_day} {current_time})")
        processed_results = filter_open_restaurants(
            current_results, 
            check_time=current_time, 
            check_day=current_day
        )
        if processed_results:
            current_results = processed_results 
            open_count = sum(1 for r in current_results if r.get('is_currently_open'))
            print(f"   ✅ Có {open_count}/{len(current_results)} quán đang mở cửa.")
        else:
            print("   ❌ Không có quán nào (Lỗi hệ thống).")
            return []

    # ===== STEP 3: FOOD FILTER (Lọc theo món ăn bằng AI) =====
    if foods and current_results:
        current_results = ai_check_food_relevance_batch(current_results, foods)        
    
    return current_results

# ------------------------------------------------------------------
# 3. POST-FILTER (Lọc giá)
# ------------------------------------------------------------------
def postfilter(filtered_results, budget=None):
    if not filtered_results: return []
    if not budget: return filtered_results
    
    # User nhập "50k" -> budget_val = 50000
    budget_val = parse_price(budget)
    if not budget_val: return filtered_results

    print(f"💰 [STEP 3] Budget Filter: Check if {budget_val} inside Restaurant Range")
    
    budget_filtered = []

    for r in filtered_results:
        price_str = str(r.get('price', ''))
        
        # Lấy khoảng giá của quán: (min_q, max_q)
        r_range = parse_price_range(price_str)
        
        # CASE 1: Quán không có giá -> Giữ lại (Unknown)
        if not r_range:
            r['estimated_price'] = "Unknown"
            budget_filtered.append(r)
            continue
            
        min_q, max_q = r_range
        
        # CASE 2: Logic user yêu cầu: Min_Quan <= Budget <= Max_Quan
        # Lưu ý: Thêm buffer 10% cho Max để đỡ bị sót nếu lố xíu (tùy ông)
        # Ví dụ: Quán 20k-55k, User 50k -> 20 <= 50 <= 55 (OK)
        if min_q <= budget_val <= (max_q * 1.1):
            r['estimated_price'] = f"{min_q}-{max_q}"
            budget_filtered.append(r)
            
    print(f"   ✅ Đúng tầm giá: {len(budget_filtered)} quán.")
    return budget_filtered

# ------------------------------------------------------------------
# 4. MAIN FUNCTION (Kết hợp pre/post filter)
# ------------------------------------------------------------------
def filter_and_split_restaurants(full_places_data, location=None, budget=None, foods=None, current_day=None, current_time=None):
    """
    Chạy toàn bộ pipeline lọc: Location, Time, Food, Budget.
    """
    main = prefilter(full_places_data, location, foods, current_day, current_time)
    return postfilter(main, budget)