import google.generativeai as genai
import os

MODEL = "gemini-2.5-flash"

API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD3b52kkvCkB3wW78NzXOWCIspO_Mk6joI") 
genai.configure(api_key=API_KEY)

def generate_response(prompt: str):
    model_instance = genai.GenerativeModel(MODEL)
    response = model_instance.generate_content(prompt)
    return response.text