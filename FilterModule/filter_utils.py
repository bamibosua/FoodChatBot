import os
import re
import json
import google.generativeai as genai
from .time_utils import filter_open_restaurants
from .price_utils import parse_price


# Dùng Flash là chuẩn bài cho tốc độ
MODEL_NAME = "gemini-2.5-flash"

def ai_check_food_relevance_batch(restaurants, food_query, api_key):
    """
    AI Filter tối ưu tốc độ (Low Latency).
    """
    if not food_query or not restaurants or not api_key: 
        return restaurants

    # 1. Rút gọn dữ liệu đầu vào tối đa (Chỉ gửi thông tin cần thiết)
    input_list = [
        {'id': i, 'n': r.get('title', ''), 't': r.get('types', [])} 
        for i, r in enumerate(restaurants)
    ]
    
    print(f"🤖 [AI FAST] Check '{food_query}' ({len(restaurants)} quán)...")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        
        # 2. PROMPT "QUÂN ĐỘI" (Ngắn, Lệnh trực tiếp, Không văn hoa)
        # Bỏ hết mấy câu "Bạn là chuyên gia...", "Hãy giúp tôi..."
        prompt = f"""
        Lọc danh sách quán khớp với món: "{food_query}".
        
        QUY TẮC BẮT BUỘC:
        1. Giữ lại: Quán bán món ăn liên quan hoặc đúng loại hình.
        2. LOẠI BỎ: 
           - Địa điểm phi thực phẩm (ATM, Shop, Cây cảnh, Tiệm thuốc).
           - Sai ngữ nghĩa (VD: tìm "cay" -> BỎ "Cây", "Cày", "Cầy").
        
        DATA: {json.dumps(input_list, ensure_ascii=False)}
        
        OUTPUT JSON ONLY: {{"ids": [list_of_valid_ids]}}
        """
        
        # 3. Config tối ưu tốc độ: Temperature = 0 (AI trả lời như cái máy, không sáng tạo)
        response = model.generate_content(
            prompt, 
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.0 # QUAN TRỌNG: Giúp phản hồi nhanh và ổn định nhất
            }
        )
        
        result_json = json.loads(response.text)
        valid_indices = result_json.get('ids', [])
        
        filtered = [restaurants[i] for i in valid_indices if i < len(restaurants)]
        print(f"   ⚡ AI chốt: {len(filtered)}/{len(restaurants)} quán.")
        return filtered

    except Exception as e:
        print(f"   ⚠️ AI Skip: {e}") 
        return restaurants

def prefilter(local_results, location=None, foods=None, current_day=None, current_time=None, api_key=None):
    print(f"\n🔍 PIPELINE START (Input: {len(local_results)} quán)")
    current_results = local_results

    # ===== STEP 1: LOCATION FILTER =====
    if location:
        print(f"📍 [STEP 1] Location Filter: '{location}'")
        location_filtered = []
        loc_lower = location.lower().strip()
        
        # A. Check Quận Số (VD: Quận 1, Q.3) - ĐÃ FIX LOGIC
        is_numeric_search = False
        target_num = None
        
        # Tìm pattern chính xác: quận/q/q./district + số
        district_match = re.search(r'\b(quận|q\.|q|district)\s*(\d+)\b', loc_lower)
        
        if district_match:
            _, target_num = district_match.groups()
            # Pattern chính xác để tránh match nhầm (ví dụ: Quận 1 vs Quận 10)
            pattern = rf"\b(quận|q\.|q|district)\s*0?{target_num}\b"
            is_numeric_search = True
            print(f"   ℹ️ Mode: Quận Số -> Tìm Q.{target_num}")
        else:
            # B. Mode Đa Từ Khóa (Tên Riêng)
            parts = re.split(r'[,;]\s*', loc_lower)
            keywords = []
            stopwords = ["thành phố", "tỉnh", "việt nam", "vietnam", "vn", "quận", "huyện", "thị xã", "phường", "xã", "tp.", "tt."]
            
            for part in parts:
                clean_part = part
                for sw in stopwords:
                    clean_part = clean_part.replace(sw, " ")
                core_word = " ".join(clean_part.split())
                if len(core_word) > 1: 
                    keywords.append(core_word)
            
            if not keywords: keywords = [loc_lower]
            print(f"   ℹ️ Mode: Đa Từ Khóa -> {keywords}")

        # C. Lọc
        for r in current_results:
            full_info = (str(r.get('address', '')) + " " + str(r.get('title', ''))).lower()
            match = False
            
            if is_numeric_search:
                if re.search(pattern, full_info): match = True
            else:
                # Logic AND: Phải chứa TẤT CẢ keywords
                match_all = True
                for kw in keywords:
                    if kw not in full_info:
                        match_all = False
                        break
                if match_all: 
                    match = True
                else:
                    # Nếu AND thất bại, thử vớt vát bằng keyword đầu tiên (quan trọng nhất)
                    # NHƯNG: Chỉ áp dụng nếu keyword đầu tiên đủ dài (>3 ký tự) để tránh rác
                    if len(keywords) > 1 and len(keywords[0]) > 3:
                         if keywords[0] in full_info:
                             match = True # Vớt vát (Relaxed)

            if match:
                location_filtered.append(r)
        
        # D. KẾT QUẢ (STRICT MODE - KHÔNG FALLBACK)
        if not location_filtered:
            print(f"⚠️ Không tìm thấy quán nào đúng địa chỉ yêu cầu.")
            # return [] # <-- Trả về rỗng để báo "Không tìm thấy"
            # TUY NHIÊN: Để tránh màn hình trắng xóa nếu Google chỉ lệch 1 xíu
            # Ta có thể check xem có phải do Zoom quá xa không?
            # Nếu input có "Vĩnh Long" mà kết quả toàn "Cần Thơ" -> Chắc chắn sai -> Return Rỗng.
            return [] 
        else:
            print(f"   ✅ Khớp Location: {len(location_filtered)}/{len(current_results)} quán.")
            current_results = location_filtered

    else:
        print("⏩ Bỏ qua Location.")


    # ===== STEP 2: TIME FILTER =====
    if current_results:
        # Gọi hàm mới (chỉ gắn nhãn chứ không lọc bỏ)
        processed_results = filter_open_restaurants(current_results, check_time=current_time, check_day=current_day)
        
        if processed_results:
            current_results = processed_results # <-- GIỮ LẠI TẤT CẢ kết quả (Mở và Đóng)
            open_count = sum(1 for r in current_results if r.get('is_currently_open'))
            print(f"   ✅ Đã gắn nhãn trạng thái mở cửa cho {len(current_results)} quán.")
            # KHÔNG RETURN NỮA, để các quán đóng đi tiếp qua Food Filter và Sorting
        else:
            print("   ❌ Không có quán nào (Lỗi hệ thống).")
            return [] # Trả về rỗng nếu có lỗi xảy ra

    # ===== STEP 3: FOOD FILTER =====
    if foods and api_key and current_results:
        current_results = ai_check_food_relevance_batch(current_results, foods, api_key)        
    
    return current_results

def postfilter(filtered_results, budget=None):
    if not filtered_results: return []
    if not budget: return filtered_results
    
    print(f"💰 [STEP 4] Budget Filter: <= '{budget}'")
    user_max_budget = parse_price(budget) or 100000
    budget_filtered = []

    for r in filtered_results:
        price_str = str(r.get('price', ''))
        r_price = parse_price(price_str)
        est_price = r_price if r_price else 50000 
        
        if est_price <= user_max_budget:
            r['estimated_price'] = est_price
            budget_filtered.append(r)
            
    print(f"   ✅ Đúng túi tiền: {len(budget_filtered)} quán.")
    return budget_filtered

def filter_and_split_restaurants(full_places_data, location=None, budget=None, foods=None, current_day=None, current_time=None, api_key=None):
    main = prefilter(full_places_data, location, foods, current_day, current_time, api_key)
    return postfilter(main, budget)