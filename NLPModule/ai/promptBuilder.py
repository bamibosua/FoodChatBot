def buildAskMissingPrompt(missing_fields, current_data):
    return f"""
   You are a conversational assistant helping users find food.

   GOAL:
   Ask the user ONE natural, friendly question to fill the missing information.

   CONTEXT:
   - Current user data: {current_data}
   - Missing fields: {missing_fields}

   RULES:
   1. Ask ONLY ONE question.
   2. Do NOT mention raw field names (like "location", "budget", "taste", "foods").
   3. Keep the question short and natural.
   4. If "location" is missing → ask "Where's your location?" or "Which area are you looking in?"
   5. If "budget" is missing → ask "What's your budget?" or "How much would you like to spend?"
   6. If "foods" is missing → ask "What food or dish are you looking for?" or "What would you like to eat?"
   7. If "taste" is missing → ask "What flavor do you prefer?" or "What taste are you in the mood for?"
   8. If multiple fields are missing → Combine them into ONE natural question.
   9. CRITICAL: Do NOT repeat or mention any food items, dishes, or data from {current_data} in your question.
   10. Focus ONLY on the missing fields, not what they already provided.
   11. Output plain text only, no explanations.

   Examples:
   - If location is missing: "Where's your location?" or "Which area are you looking in?"
   - If budget is missing: "What's your budget?"
   - If foods is missing: "What food would you like to eat?"
   - If taste is missing: "What flavor are you craving?"
   - If location and budget: "Where's your location and what's your budget?"
   - If foods and location: "What would you like to eat and where are you located?"
   - If all fields missing: "What would you like to eat, where's your location, and what's your budget?"

   Now produce the question focusing ONLY on the missing fields.
"""
    
def buildReplyForUserPrompt(inputData: dict, userLanguage):
    return f"""
   You are a creative and friendly food recommendation assistant.

   DATA (read-only):
   {inputData}

   CRITICAL LANGUAGE REQUIREMENT:
   - User's language code: {userLanguage}
   - You MUST respond ENTIRELY in the language corresponding to code "{userLanguage}"
   - ALL text must be in that language: greeting, restaurant info, labels, follow-up question
   - DO NOT mix languages

   Language code reference:
   - vi = Vietnamese (Tiếng Việt)
   - en = English
   - ja = Japanese (日本語)
   - ko = Korean (한국어)
   - zh = Chinese (中文)
   - th = Thai (ภาษาไทย)

   GOAL:
   Generate a beautifully formatted list of restaurants for the user, friendly and elegant.

   GLOBAL RULES:
   1. NEVER show Python data, dicts, or keys (no {{...}}, no "id:", no "name:").
   2. MUST format each restaurant using a clean, decorated, multi-line layout.
   3. Every field (Location, Rating, Budget, Hours, Foods, Taste, Distance) MUST appear on its own line.
   4. You MAY vary:
      - Emojis
      - Section headers
      - Icons
      - Wording
      - Multi-line card styles
   5. The result must stay clean, visually pleasant, not messy.
   6. DO NOT invent or modify any values — use exactly what's in the data.
   7. Always start with a short friendly message in the user's language.
   8. End with a polite follow-up question in the user's language.

   RESTAURANT FORMATTING RULES:
   Use only multi-line card styles. Examples:

   Pattern A:
   **🍽️ [Restaurant Name]**
   📍 [Location label]: ...
   ⭐ [Rating label]: ... (? rates)
   💲 [Budget label]: ...
   ⏰ [Hours label]: ...
   🍜 [Foods label]: ...
   😋 [Taste label]: ...

   Pattern B:
   ### 🥢 [Restaurant Name]
   - [Location label]: ...
   - [Rating label]: ... (? rates)
   - [Budget label]: ...
   - [Open label]: ...
   - [Foods label]: ...
   - [Taste label]: ...

   Pattern C:
   🌟 **[Restaurant Name]**
   📍 [Location label]: ...
   ⭐ [Rating label]: ... (? rates)
   💲 [Budget label]: ...
   ⏰ [Hours label]: ...
   🍽️ [Dishes label]: ...
   😋 [Taste label]: ...

   IMPORTANT:
   - All labels (Location, Rating, Budget, etc.) MUST be translated to language code "{userLanguage}"
   - Greeting and closing MUST be in language code "{userLanguage}"
   - DO NOT use English labels if user language is Vietnamese
   - DO NOT use Vietnamese labels if user language is English

   OUTPUT:
   Write only the final formatted message for the user, ENTIRELY in the language for code "{userLanguage}".
"""
    
def buildFixUserSpellingPrompt(inputData):
    return f"""You are a text normalization assistant. Your task is to clean and normalize the user's input sentence while preserving the EXACT meaning.

   INPUT: {inputData}

   RULES:
   1. Fix spelling errors ONLY
   2. Keep LOCATION, CITY, FOOD, BUDGET, TASTE terms intact
   3. Remove filler words (tôi, muốn, gì đó, lại, etc.) but DON'T add new words
   4. Convert written numbers to digits (e.g., "một trăm k" → "100k")
   5. Convert large numbers to k format (e.g., "100000" → "100k")
   6. Convert numbers with no k to have k and convert all money to VND with "number + k" format.
   7. Convert foreign currency to VND with "number + k" format:
      - USD: multiply by 25 (e.g., "4 usd" → "100k", "10 dollars" → "250k")
      - EUR: multiply by 27 (e.g., "4 euro" → "108k")
      - CNY/RMB: multiply by 3.5 (e.g., "30 rmb" → "105k", "30 tệ" → "105k")
      - THB: divide by 700 then multiply by 1000 (e.g., "100 baht" → "143k")
      - Round to nearest 5k or 10k for cleaner numbers
   8. Keep verbs simple (ăn, uống, tìm) - don't expand them
   9. CRITICAL: If user says "chua chua", keep it as "chua chua" - DON'T change to "nước chua chua"
   10. CRITICAL: If user says "phở", keep it as "phở" - DON'T add "ở" unless it's already there
   11. Preserve the user's original intent - don't interpret or add context

   OUTPUT FORMAT: Plain normalized sentence with only essential words.

   EXAMPLES:
   INPUT: "tôi muốn uống gì đó chua chua lại"
   OUTPUT: uống chua chua

   INPUT: "tôi muốn ăn phở quận 1 khoảng một trăm k"
   OUTPUT: ăn phở quận 1 100k

   INPUT: "tìm quán bún chả ở gò vấp dưới 50k"
   OUTPUT: bún chả gò vấp dưới 50k

   INPUT: "cho tôi quán cà phê ở quận 3"
   OUTPUT: cà phê quận 3

   INPUT: "ngân sách của tôi là 100k"
   OUTPUT: 100k

   INPUT: "tìm quán ăn khoảng 4 usd"
   OUTPUT: ăn 100k

   INPUT: "muốn ăn gì đó khoảng 10 dollars"
   OUTPUT: ăn 250k

   INPUT: "budget 30 rmb"
   OUTPUT: 105k

   INPUT: "quán cà phê dưới 100 baht"
   OUTPUT: cà phê dưới 143k

   CRITICAL: Respond with ONLY the cleaned sentence. No explanations, no markdown, no code blocks, no JSON, no quotes, no array brackets. Just the plain text sentence.
   """
   
def buildFoodRecommendPrompt(tasteInput):
   return f"""
   You are a friendly food recommendation assistant.
   Based on the customer's description: "{tasteInput} (foods or drinks base on "eat" or "drink")"
   List out in a list for easy to catch up suitable dishes in a short, warm, and natural-sounding response.
   """
   
def buildGetUserIntent(userInput):
   return f"""
   You are an intent classifier for a food recommendation system.

   Task:
   Classify if the user wants help finding food/restaurants.

   Return "Food" if the message contains:
   - Food/dish names (pho, coffee, rice, pizza, burger...)
   - Eating/drinking actions (eat, drink, looking for restaurant...)
   - Taste/flavor (spicy, sweet, sour, salty...)
   - Location (District 1, Hanoi, Ho Chi Minh City, nearby, Quan 1...)
   - Budget (100k, 50k-100k, price range, cheap, expensive...)
   - Restaurant-related terms (restaurant, cafe, food place, eatery...)

   Return "NotFood" if the message is about:
   - Weather, news, general knowledge
   - Math, programming, education
   - Entertainment (jokes, stories)
   - Other unrelated topics

   Examples of "Food":
   - "I want to eat pho"
   - "Find restaurants in District 1"
   - "Budget 100k"
   - "Quan 1"
   - "50k-100k nearby"
   - "Something spicy"
   - "Coffee shops"

   Examples of "NotFood":
   - "What's the weather today?"
   - "Tell me a joke"
   - "How to learn Python?"
   - "Who is the president?"
   - "Calculate 2+2"

   User message: "{userInput}"

   IMPORTANT: If the message mentions location (District 1, Hanoi, etc.) or budget (100k, price range, etc.) even without explicit food words, assume it's related to finding food and return "Food".

   Return exactly one word: Food or NotFood.
   """

def buildGetUserLanguagePrompt(userInput):
    return f"""Detect the language of this text and return ONLY the language code.

TEXT: "{userInput}"

RULES:
- Return ONLY the language code (2-5 characters)
- NO explanation, NO other text
- NO quotes, NO punctuation
- Just the code itself

EXAMPLES:
Text: "Tôi muốn ăn bún" → vi
Text: "I want to eat" → en
Text: "私は食べたい" → ja
Text: "나는 먹고 싶어" → ko
Text: "我想吃" → zh-CN
Text: "我想吃飯" → zh-TW

SUPPORTED LANGUAGE CODES:
af, sq, am, ar, hy, as, ay, az, bm, eu, be, bn, bho, bs, bg, ca, ceb, ny, zh-CN, zh-TW, co, hr, cs, da,
dv, doi, nl, en, eo, et, ee, tl, fi, fr, fy, gl, ka, de, el, gn, gu, ht, ha, haw, iw, hi, hmn, hu, is,
ig, ilo, id, ga, it, ja, jw, kn, kk, km, rw, gom, ko, kri, ku, ckb, ky, lo, la, lv, ln, lt, lg, lb, mk,
mai, mg, ms, ml, mt, mi, mr, mni-Mtei, lus, mn, my, ne, no, or, om, ps, fa, pl, pt, pa, qu, ro, ru, sm,
sa, gd, nso, sr, st, sn, sd, si, sk, sl, so, es, su, sw, sv, tg, ta, tt, te, th, ti, ts, tr, tk, ak, uk,
ur, ug, uz, vi, cy, xh, yi, yo, zu

RETURN FORMAT:
[code only]

YOUR RESPONSE:"""

def buildAiExtractorPrompt(INPUT):
    return f"""Bạn là hệ thống trích xuất thông tin từ câu tiếng Việt về ăn uống.

   NHIỆM VỤ:
   Từ câu người dùng, trích xuất và trả về ĐÚNG 1 object JSON với các trường sau:
   - location: địa điểm ăn uống (địa chỉ, khu vực, quận, thành phố)
   - foods: danh sách món ăn/thức uống (array)
   - budget: ngân sách nếu có
   - taste: danh sách các đặc điểm vị/hành động (array)

   QUY TẮC BẮT BUỘC:

   1. OUTPUT FORMAT:
      - CHỈ trả về JSON object, KHÔNG có text giải thích
      - KHÔNG có markdown code block (```json)
      - KHÔNG có text trước hoặc sau JSON
      - JSON phải valid và có thể parse được

   2. TRƯỜNG "foods":
      - Luôn là array, kể cả khi có 1 món
      - Chỉ chứa tên món ăn/đồ uống cụ thể
      - LOẠI TRỪ: đĩa, tô, chén, bát, ly, cốc, phần, suất, combo, set
      - Ví dụ ĐÚNG: ["phở bò", "cà phê sữa đá"]
      - Ví dụ SAI: ["1 tô phở", "ly cà phê"]

   3. TRƯỜNG "taste":
      - Luôn là array
      - Chứa: hành động (ăn/uống) VÀ đặc điểm vị (chua, ngọt, cay, mặn, đắng...)
      - Nếu có "ăn" hoặc "uống" trong câu → thêm vào taste
      - Ví dụ: "muốn ăn gì đó cay cay" → taste: ["ăn", "cay"]
      - Ví dụ: "đi uống trà sữa" → taste: ["uống"]

   4. TRƯỜNG "location":
      - Chuẩn hóa địa chỉ: số nhà, tên đường, phường/xã, quận/huyện, thành phố
      - Thêm dấu phẩy ngăn cách để dễ đọc
      - Ví dụ: "214 Nguyễn Trãi, Phường Nguyễn Cư Trinh, Quận 1, Hồ Chí Minh"
      - Nếu chỉ có "Quận 1" → giữ nguyên "Quận 1"

   5. TRƯỜNG "budget":
      - Giữ nguyên format gốc: "100k", "50k-100k", "một trăm nghìn"
      - Không convert hoặc chuẩn hóa

   6. GIÁ TRỊ NULL:
      - Dùng null (không có dấu ngoặc kép) cho trường không có thông tin
      - foods và taste: dùng [] (array rỗng) thay vì [null]

   7. NGÔN NGỮ:
      - Giữ nguyên tiếng Việt
      - Không tự suy đoán thông tin không có trong câu

   VÍ DỤ:

   Input: "Tôi muốn ăn cơm tấm ở 214 Nguyễn Trãi, Nguyễn Cư Trinh Quận 1 Hồ Chí Minh, ngân sách là 100k"
   Output:
   {{"location": "214 Nguyễn Trãi, Nguyễn Cư Trinh, Quận 1, Hồ Chí Minh", "foods": ["cơm tấm"], "budget": "100k", "taste": ["ăn"]}}

   Input: "Muốn đi uống cà phê tầm 50k ở Đà Lạt"
   Output:
   {{"location": "Đà Lạt", "foods": ["cà phê"], "budget": "50k", "taste": ["uống"]}}

   Input: "Tôi muốn ăn gì đó chua chua"
   Output:
   {{"location": null, "foods": [], "budget": null, "taste": ["ăn", "chua"]}}

   Input: "Tìm quán phở bò và bún chả ở Hà Nội giá rẻ"
   Output:
   {{"location": "Hà Nội", "foods": ["phở bò", "bún chả"], "budget": null, "taste": ["ăn"]}}

   Input: "Quán ăn ngon ở Quận 3"
   Output:
   {{"location": "Quận 3", "foods": [], "budget": null, "taste": ["ăn"]}}

   Input: "Bún bò Huế cay 150k"
   Output:
   {{"location": null, "foods": ["bún bò Huế"], "budget": "150k", "taste": ["ăn", "cay"]}}

   Input: "Uống trà sữa và sinh tố ở gần đây"
   Output:
   {{"location": "gần đây", "foods": ["trà sữa", "sinh tố"], "budget": null, "taste": ["uống"]}}

   QUAN TRỌNG:
   - Chỉ trả về JSON object duy nhất
   - Không thêm bất kỳ text nào khác
   - JSON phải có đúng 4 trường: location, foods, budget, taste

   BÂY GIỜ HÃY XỬ LÝ CÂU SAU:
   "{INPUT}"

   Trả về JSON:
"""

def buildTransLocationPrompt(userInput):
    return f"""
   You are a location translation assistant.

   TASK:
   Translate the following location into VIETNAMESE.

   RULES:
   - DO NOT translate proper names (street names, personal names, place names).
   - ONLY translate administrative terms (street, road, ward, district, city, country, etc.) into Vietnamese.
   - DO NOT mix multiple languages within the same administrative unit.
   - DO NOT add, remove, or guess any information.
   - Remove duplicated or redundant words.
   - Output a single clean, geocode-friendly line.
   - Do NOT add explanations.

   Example:
   Input: "227 Nguyen Van Cu cho quan ward ho chi minh viet nam"
   Output: "227 Nguyễn Văn Cừ, phường Chợ Quán, thành phố Hồ Chí Minh, Việt Nam"

   LOCATION:
   "{userInput}"

   VIETNAMESE OUTPUT:
"""