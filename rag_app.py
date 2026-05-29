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


def test_gemini(prompt: str = "Hello! Please respond in one short sentence.") -> dict:
    """
    Verify the Gemini API integration by sending a test prompt and returning the response.

    Steps:
    1. Confirm the API key was loaded and the client was created at startup.
    2. Send the prompt to the configured Gemini model.
    3. Return the model name, prompt, and generated answer as a dictionary.
    """
    if not client:
        raise ValueError("GEMINI_API_KEY not configured")

    response = client.models.generate_content(model=MODEL, contents=prompt)
    return {"model": MODEL, "prompt": prompt, "answer": response.text}


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "RAG App is running!"}


@app.get("/test-gemini")
def test_gemini_endpoint():
    """HTTP endpoint that runs test_gemini() so the integration can be verified in a browser."""
    try:
        result = test_gemini()
        return {"status": "ok", **result}
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except genai_errors.ClientError as e:
        raise HTTPException(status_code=e.code, detail=e.message or str(e))
    except genai_errors.APIError as e:
        raise HTTPException(status_code=e.code or 502, detail=e.message or str(e))


@app.get("/chat/")
def chat(prompt: str):
    """Accept a custom prompt and return Gemini's answer using the same logic as test_gemini()."""
    try:
        result = test_gemini(prompt=prompt)
        return {"question": result["prompt"], "answer": result["answer"]}
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except genai_errors.ClientError as e:
        raise HTTPException(status_code=e.code, detail=e.message or str(e))
    except genai_errors.APIError as e:
        raise HTTPException(status_code=e.code or 502, detail=e.message or str(e))
