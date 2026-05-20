import os
from fastapi import FastAPI
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from the .env file
load_dotenv()

app = FastAPI()

# Fetch the configured key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ API Key missing from .env file")
else:
    genai.configure(api_key=api_key)
    print("✅ Gemini API successfully connected!")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "RAG App is running!"}
