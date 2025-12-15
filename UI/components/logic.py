#logic.py
from NLPModule.NLPModule import analyzeUserInput, replyMissingFields, reply, replyRecommendFood, userIntentClassification
from FilterModule.app_runner import run_app
from Translator.translator import get_original_language

def parse_user_input(user_input):
    intent = userIntentClassification(user_input)
    original_lang = get_original_language(user_input)
    if intent == "NotFood":
        not_food_message = (
            "Xin lỗi, tôi chỉ hỗ trợ tìm kiếm quán ăn. Bạn có thể hỏi tôi về món ăn, nhà hàng hoặc quán ăn bạn muốn tìm."
            if original_lang == "vi"
            else "Sorry, I only support finding restaurants and food. You can ask me about dishes, restaurants or places to eat you're looking for."
        )
        return {"intent": "NotFood", "message": not_food_message}, original_lang
    
    parsed = analyzeUserInput(user_input)
    print(f"Debug detect language logic parse user:{original_lang}")
    return parsed, original_lang

# Xử lý logic, check dữ liệu, chỉ chạy 1 lần
def process_logic(parsed_data, original_lang, final_data):
    print(f"🔍 parsed_data KEYS: {parsed_data.keys()}")
    print(f"🔍 parsed_data: {parsed_data}")
    print(f"🔍 final_data BEFORE update: {final_data}")
    
    # update final_data với parsed_data 
    for key in final_data: 
        if parsed_data.get(key) not in (None, "null", []): 
            final_data[key] = parsed_data[key]
    
    print(f"🔍 final_data AFTER update: {final_data}")
    # update final_data với parsed_data 
    for key in final_data: 
        if parsed_data.get(key) not in (None, "null", []): 
            final_data[key] = parsed_data[key] 

 
    taste_empty = final_data.get("taste") in (None, "null", [])
    foods_empty = final_data.get("foods") in (None, "null", [])
 
    # Tính missing fields (loại trừ taste và foods)
    missing_fields = [ 
        k 
        for k, v in final_data.items() 
        if k not in ("taste", "foods") and v in (None, "null", [], {})
    ]
    
    print(f"🔍 DEBUG missing_fields: {missing_fields}")
    print(f"🔍 DEBUG taste_empty: {taste_empty}, foods_empty: {foods_empty}")

    if taste_empty and foods_empty:
        if missing_fields:
            # Trường hợp: Thiếu foods, taste VÀ các trường khác
            # Thêm foods và taste vào missing_fields
            missing_fields.append('foods')
            missing_fields.append('taste')
            
            # Gọi bot hỏi tất cả missing fields
            bot_reply = replyMissingFields(missing_fields, final_data, original_lang)
            
            # Xóa foods và taste ra khỏi missing_fields sau khi hỏi
            missing_fields.remove('foods')
            missing_fields.remove('taste')
        else:
            # Trường hợp: CHỈ thiếu foods và taste, các trường khác đầy đủ
            # Gọi bot hỏi riêng foods và taste
            bot_reply = replyMissingFields(['foods', 'taste'], final_data, original_lang)
        
        return {"bot_reply": bot_reply, "missing_fields": missing_fields, "processed_data": None}
    if not taste_empty and not foods_empty:
        # Lấy danh sách foods và tastes
        foods = final_data.get('foods', [])
        tastes = final_data.get('taste', [])

        # Gộp taste vào food
        combined_foods = foods + tastes
        final_data['foods'] = combined_foods

        # Xóa taste khỏi final_data
        if 'taste' in final_data:
            del final_data['taste']

        # Update các biến check
        taste_empty = True
        foods_empty = False
 
    # Nếu có taste nhưng thiếu các field khác → recommend món ăn
    if not taste_empty and missing_fields:
        bot_reply = replyRecommendFood(final_data, original_lang)
        return {"bot_reply": bot_reply, "missing_fields": None, "processed_data": None}
    
    # Nếu có taste nhưng thiếu foods (và đủ các field khác) → recommend món ăn
    if not taste_empty and foods_empty:
        bot_reply = replyRecommendFood(final_data, original_lang)
        return {"bot_reply": bot_reply, "missing_fields": None, "processed_data": None}
    
    # Nếu có foods nhưng thiếu các field khác → hỏi missing
    if not foods_empty and missing_fields:
        reply_text = replyMissingFields(missing_fields, final_data, original_lang) 
        return {"bot_reply": reply_text, "missing_fields": missing_fields, "processed_data": None}
 
    # Xóa taste và map city -> location trước khi chạy run_app
    final_data_for_app = {k: v for k, v in final_data.items() if k != "taste"}
    
    # Đủ hết → chạy run_app
    processed_data = run_app(final_data_for_app) 
         
    return {"bot_reply": None, "missing_fields": None, "processed_data": processed_data}

# Tạo output
def generate_reply(processed_result, original_lang):
    if processed_result["bot_reply"]:
        return processed_result["bot_reply"]
    return reply(processed_result["processed_data"], original_lang)
