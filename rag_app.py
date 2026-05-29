import os

from fastapi import FastAPI, HTTPException

from dotenv import load_dotenv

from google import genai

from google.genai import errors as genai_errors



load_dotenv()



app = FastAPI()



api_key = os.getenv("GEMINI_API_KEY")

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")



client = genai.Client(api_key=api_key) if api_key else None



if client:

    print("Gemini API successfully connected!")

else:

    print("API Key missing from .env file")





@app.get("/health")

def health_check():

    return {"status": "ok", "message": "RAG App is running!"}





@app.get("/chat/")

def chat(prompt: str):

    if not client:

        raise HTTPException(status_code=503, detail="GEMINI_API_KEY not configured")



    try:

        response = client.models.generate_content(model=MODEL, contents=prompt)

        return {"question": prompt, "answer": response.text}

    except genai_errors.ClientError as e:

        raise HTTPException(status_code=e.code, detail=e.message or str(e))

    except genai_errors.APIError as e:
        raise HTTPException(status_code=e.code or 502, detail=e.message or str(e))


