import json
import re
import streamlit as st
from Module1.promptBuilder import buildExtractPrompt, buildAskMissingPrompt
from ollama import Client

# ====== Khởi tạo Client ======
MODEL = "gpt-oss:20b"
client = Client(host="https://kbkyo-35-185-177-234.a.free.pinggy.link")

# ====== Hàm phân tích input ======
def analyzeUserInput(userInput: str):
    response = client.chat(
        model = MODEL,
        messages = [{"role": "user", "content": buildExtractPrompt(userInput)}],
    )
    
    rawAIResponse = response["message"]["content"].strip()

    match = re.search(r"\{.*\}", rawAIResponse, flags=re.DOTALL)
    if not match:
        raise ValueError("Không tìm thấy đối tượng JSON.")

    json_text = match.group(0)
        
    AIExtractor = json.loads(json_text)

    location = AIExtractor.get("location_ai")
    taste = AIExtractor.get("tasteAndFood_ai")
    budget = AIExtractor.get("budget_raw")

    if location in ("null", "", "None"): location = None
    if budget in ("null", "", "None"): budget = None
    if not isinstance(taste, list): taste = []

    return {
        "location": location,
        "taste": taste,
        "budget": budget,
    }
    
def askAiForMissingFields(missingFields, currentData):
    response = client.chat(
        model=MODEL,
        messages=[{"role": "user", "content": buildAskMissingPrompt(missingFields, currentData)}]
    )
    return response.message['content']