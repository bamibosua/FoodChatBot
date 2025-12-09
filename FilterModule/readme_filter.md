pip install google-generativeai

Thắc mắc :
- Tại sao chỉ lấy 20 quán :
Vấn đề này là do Google Maps API (thông qua SerpAPI) mặc định phân trang (pagination) mỗi lần trả về chỉ 20 kết quả để tiết kiệm tài nguyên. Muốn lấy nhiều hơn, ta phải chạy vòng lặp để "lật trang" (Page 1, Page 2, Page 3...).

⚠️ CẢNH BÁO TIỀN API: Mỗi lần "lật trang" tính là 1 lượt tìm kiếm.

Lấy 20 quán = 1 Credit.

Lấy 60 quán = 3 Credits.

Lấy full (ví dụ 100 quán) = 5 Credits.

Dưới đây là bản nâng cấp cho data_utils.py để tự động lật trang và lấy tối đa 60 quán (bạn có thể chỉnh số này).

 # Location "Đống Đa, Hà Nội" lỗi đéo biết đường fix

 Lỗi nhà do khác biệt và param 2 phiên bản Quốc tế và Việt Nam của Google Maps





 # filter_utils.py
import os
import json
import re
import google.generativeai as genai
from time_utils import filter_open_restaurants
from price_utils import parse_price

os.environ['GRPC_VERBOSITY'] = 'NONE'
os.environ['GLOG_minloglevel'] = '3'

MODEL_NAME = "gemini-2.5-flash"

# ------------------------------------------------------------------
# 1. HÀM AI LỌC MÓN ĂN (Giữ nguyên logic cũ nhưng tối ưu prompt)
# ------------------------------------------------------------------
def ai_check_food_relevance_batch(restaurants, food_query, api_key):
    if not food_query or not restaurants: return restaurants
    
    # Rút gọn data gửi AI để tiết kiệm token
    input_list = [{'id': i, 'n': r.get('title'), 't': r.get('type')} 
                  for i, r in enumerate(restaurants)]
    
    print(f"🤖 [AI FOOD] Đang lọc '{food_query}' cho {len(restaurants)} quán...")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        
        prompt = f"""
        User muốn ăn: "{food_query}".
        Danh sách quán: {json.dumps(input_list, ensure_ascii=False)}
        
        Nhiệm vụ:
        1. Trả về danh sách 'id' của các quán bán món này hoặc liên quan.
        2. Loại bỏ các địa điểm KHÔNG PHẢI LÀ QUÁN ĂN (VD: ATM, Công ty, Shop quần áo...).
        
        Output JSON: {{"ids": [0, 2, 5]}}
        """
        
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        data = json.loads(response.text)
        indices = data.get('ids', [])
        
        return [restaurants[i] for i in indices if i < len(restaurants)]
    except Exception as e:
        print(f"⚠️ AI Food Error: {e}. Giữ nguyên danh sách.")
        return restaurants

def prefilter(local_results, location=None, foods=None, current_day=None, current_time=None, api_key=None):
    print(f"\n🔍 PIPELINE START (Input: {len(local_results)} quán)")
    current_results = local_results

    # ===== STEP 1: LOCATION FILTER (Xử lý chuỗi thông minh) =====
    if location:
        print(f"📍 [STEP 1] Location Filter: '{location}'")
        location_filtered = []
        
        # 1. Chuẩn hóa & Tách Input
        loc_lower = location.lower().strip()
        
        # 2. KIỂM TRA LOẠI TỪ KHÓA
        # Nếu có số quận (VD: "quận 1", "q.3") -> Dùng Regex Số
        district_nums = re.findall(r'\d+', loc_lower)
        is_numeric_search = False
        
        if district_nums and ("q" in loc_lower or "district" in loc_lower or "phường" in loc_lower):
            target_num = district_nums[0]
            # Regex: Tìm chữ "quận/q/p" đi kèm với số đó
            # \b chặn biên để 1 không dính 10
            pattern = rf"(quận|q\.|q|district|p\.|phường)\s*0?{target_num}\b"
            is_numeric_search = True
            print(f"   ℹ️ Mode: Quận Số (Tìm Q.{target_num})")
        
        # Nếu là tên chữ (VD: "Thanh Bình, Đồng Tháp") -> Dùng Multi-Keyword
        else:
            # Tách thành các phần nhỏ (VD: "thanh bình", "đồng tháp")
            parts = re.split(r'[,;]\s*', loc_lower)
            keywords = []
            
            stopwords = [
                "thành phố", "tỉnh", "việt nam", "vietnam", "vn",
                "quận", "huyện", "thị xã", "phường", "xã",
                "tp.", "tt.", "h.", "p.", "x."
            ]
            
            for part in parts:
                clean_part = part
                for sw in stopwords:
                    clean_part = clean_part.replace(sw, " ")
                
                # Gọt sạch khoảng trắng
                core_word = " ".join(clean_part.split())
                if len(core_word) > 1: # Bỏ từ quá ngắn
                    keywords.append(core_word)
            
            if not keywords: # Fallback nếu lỡ xóa hết
                keywords = [loc_lower]
                
            print(f"   ℹ️ Mode: Đa Từ Khóa -> {keywords}")

        # 3. LỌC DANH SÁCH
        for r in current_results:
            full_info = (str(r.get('address', '')) + " " + str(r.get('title', ''))).lower()
            match = False
            
            if is_numeric_search:
                # Tìm theo Regex Số
                if re.search(pattern, full_info):
                    match = True
            else:
                # Tìm theo Đa Từ Khóa (Logic AND: Phải chứa TẤT CẢ keywords)
                # VD: Phải có "thanh bình" VÀ "đồng tháp"
                match_all = True
                for kw in keywords:
                    if kw not in full_info:
                        match_all = False
                        break
                if match_all:
                    match = True
            
            if match:
                location_filtered.append(r)
        
        # 4. FAIL-SAFE (Quan trọng)
        if not location_filtered:
            print(f"⚠️ Không tìm thấy quán nào khớp tiêu chí.")
            # Nếu tìm tên riêng (keywords) mà không thấy -> Trả về list gốc (Geocode đã đúng vùng)
            # Nhưng nếu tìm Quận số (numeric) mà không thấy -> Có thể sai thật, trả về rỗng hoặc list gốc tùy bạn
            # Ở đây chọn an toàn: Trả về list gốc để người dùng tự lọc bằng mắt
            print(f"   👉 Fallback: Giữ lại toàn bộ {len(current_results)} quán (vì Geocode đã đúng vùng).")
        else:
            print(f"   ✅ Khớp Location: {len(location_filtered)}/{len(current_results)} quán.")
            current_results = location_filtered

    else:
        print("⏩ Bỏ qua Location (Không có input).")
        
    # ===== STEP 2: TIME FILTER =====
    print(f"⏰ [STEP 2] Time Filter: {current_day} {current_time}")
    if current_results:
        time_filtered = filter_open_restaurants(
            current_results, 
            check_time=current_time, 
            check_day=current_day
        )
        if time_filtered:
            current_results = time_filtered
            print(f"   ✅ Đang mở cửa: {len(current_results)} quán.")
        else:
            print("   ❌ Không có quán nào mở cửa.")
            return []

    # ===== STEP 3: FOOD FILTER (AI hoặc Keyword) =====
    # Hiện tại đang để AI, nếu muốn nhanh nữa thì comment dòng dưới đi
    if foods and api_key and current_results:
        # Nếu muốn dùng AI lọc món:
        # current_results = ai_check_food_relevance_batch(current_results, foods, api_key)
        
        # Nếu muốn dùng Keyword lọc món (Siêu nhanh):
        # food_clean = foods.lower()
        # current_results = [r for r in current_results if food_clean in (r.get('title','')+str(r.get('types',''))).lower()]
        pass 
    
    return current_results

# ------------------------------------------------------------------
# 4. POST FILTER (Lọc giá)
# ------------------------------------------------------------------
def postfilter(filtered_results, budget=None):
    if not filtered_results: return []
    if not budget: return filtered_results
    
    print(f"💰 [STEP 4] Budget Filter: <= '{budget}'")
    user_max_budget = parse_price(budget) or 100000
    budget_filtered = []

    for r in filtered_results:
        price_str = str(r.get('price', ''))
        r_price = parse_price(price_str)
        est_price = r_price if r_price else 50000 # Mặc định 50k nếu không có giá
        
        if est_price <= user_max_budget:
            r['estimated_price'] = est_price
            budget_filtered.append(r)
            
    print(f"   ✅ Đúng túi tiền: {len(budget_filtered)} quán.")
    return budget_filtered

# ------------------------------------------------------------------
# 5. MAIN FUNCTION
# ------------------------------------------------------------------
def filter_and_split_restaurants(full_places_data, location=None, budget=None, foods=None, current_day=None, current_time=None, api_key=None):
    # Pipeline: AI Location -> Time Check -> AI Food -> Budget
    main_res = prefilter(full_places_data, location, foods, current_day, current_time, api_key)
    final_res = postfilter(main_res, budget)
    return final_res


# price_utils.py
import re

def parse_price(price_str):
    """
    Chuẩn hóa chuỗi giá thành số nguyên (lấy giá trị Max/Upper Bound).
    VD: "100-200 N ₫" -> 200000
    VD: "1-100.000 ₫" -> 100000
    """
    if not price_str:
        return None
    
    # 1. Loại bỏ ký tự lạ, giữ lại số, dấu chấm, gạch ngang
    # Thay dấu phẩy thành dấu chấm để float() hiểu
    clean_str = re.sub(r'[^\d\.\-]', '', price_str.lower().replace(',', '.'))
    
    if not clean_str:
        return None

    try:
        # 2. Tìm tất cả các số trong chuỗi
        prices = [float(p) for p in re.findall(r'\d+\.?\d*', clean_str)]
        
        if not prices:
            return None
        
        # 3. Lấy giá trị lớn nhất (Upper bound)
        max_price = max(prices)
        
        # 4. Logic fix đơn vị: 
        # Nếu giá < 1000 (VD: 200), thường là đơn vị nghìn đồng (200k) -> nhân 1000
        # Nếu giá > 1000 (VD: 50000), giữ nguyên
        if max_price < 1000:
             return int(max_price * 1000)
        
        return int(max_price)
    
    except Exception:
        return None