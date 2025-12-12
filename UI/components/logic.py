
#logic.py
from NLPModule.NLPModule import analyzeUserInput, replyMissingFields, isInHCMMain, reply
from FilterModule.app_runner import run_app
from Translator.translator import get_original_language, translate_text

def parse_user_input(user_input):
    parsed = analyzeUserInput(user_input)
    original_lang = get_original_language(user_input)
    return parsed, original_lang

# 2️. Xử lý logic, check dữ liệu, chỉ chạy 1 lần
def process_logic(parsed_data, original_lang, final_data, city):
    # update final_data với parsed_data
    for key in final_data:
        if parsed_data.get(key) not in (None, "null", []):
            final_data[key] = parsed_data[key]

    if parsed_data.get("city") not in (None, "null", []):
        city = parsed_data["city"]

    taste_empty = final_data.get("taste") in (None, "null", [])
    foods_empty = final_data.get("foods") in (None, "null", [])

    missing_fields = [
        k
        for k, v in final_data.items()
        if (
            (k in ("taste", "foods") and taste_empty and foods_empty)
            or (k not in ("taste", "foods") and v in (None, "null", [], {}))
        )
    ]

    # Check HCM
    if not isInHCMMain(city):
        bot_reply = "Currently, the system only supports Ho Chi Minh City.\n"
        bot_reply += "Please enter a location within Ho Chi Minh City."
        if original_lang != 'en':
            bot_reply = translate_text(bot_reply, dest_lang=original_lang)
        return {"bot_reply": bot_reply, "missing_fields": None, "processed_data": None}

    # Nếu thiếu field
    if missing_fields:
        reply_text = replyMissingFields(missing_fields, final_data, original_lang)
        return {"bot_reply": reply_text, "missing_fields": missing_fields, "processed_data": None}

    # Xử lý app nặng
    processed_data = run_app(final_data)
        
    return {"bot_reply": None, "missing_fields": None, "processed_data": processed_data}

# 3️⃣ Tạo output
def generate_reply(processed_result, original_lang):
    if processed_result["bot_reply"]:
        return processed_result["bot_reply"]
    return reply(processed_result["processed_data"], original_lang)
