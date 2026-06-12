import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

load_dotenv()

app = FastAPI()


class QueryRequest(BaseModel):
    question: str


def validate_user_input(text: str):
    """Reject bad input early, before any AI model call is made."""
    if text is None or text.strip() == "":
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if len(text) < 5:
        raise HTTPException(status_code=400, detail="Question is too short")

    if len(text) > 500:
        raise HTTPException(status_code=400, detail="Question is too long")


def validate_model_output(text: str | None):
    """Ensure the AI's response is usable before returning it to the user."""
    if text is None or text.strip() == "":
        raise HTTPException(status_code=500, detail="AI returned an empty response")

    if len(text) < 10:
        raise HTTPException(status_code=500, detail="AI response is too short")

api_key = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=api_key) if api_key else None

if client:
    print("Gemini API successfully connected!")
else:
    print("API Key missing from .env file")


def test_gemini(prompt: str = "Explain how photosynthesis works in simple terms.") -> dict:
    """
    Run a two-step Gemini flow: outline first, then expand into a full answer.

    Step 1 — Generate a short outline for the user's question.
    Step 2 — Use that outline to produce the final response returned to the client.
    """
    if not client:
        raise ValueError("GEMINI_API_KEY not configured")

    outline_prompt = (
        f"Generate a short bullet-point outline (3-5 points) for answering: {prompt}"
    )
    outline_response = client.models.generate_content(model=MODEL, contents=outline_prompt)
    outline = outline_response.text
    print(f"[Step 1 outline]\n{outline}")

    expand_prompt = (
        f"Using this outline:\n{outline}\n\n"
        f"Write a clear, complete answer to: {prompt}"
    )
    final_response = client.models.generate_content(model=MODEL, contents=expand_prompt)

    return {"model": MODEL, "prompt": prompt, "answer": final_response.text}


def review_model_output(original_answer: str) -> str:
    """
    Second AI model call: review the first model's answer and improve it if needed.

    First model: answers the question.
    Second model: checks and improves the answer before it reaches the user.
    """
    review_prompt = f"""
You are reviewing an AI-generated response.

Your job:
- If the response is unclear, incomplete, or poorly written, improve it.
- If the response is already good, return it unchanged.

Important: output ONLY the final response text itself.
Do not add commentary, explanations, or notes about your review.

AI response to review:
{original_answer}
"""
    if not client:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY not configured")

    review_response = client.models.generate_content(model=MODEL, contents=review_prompt)
    return review_response.text or original_answer


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


@app.post("/query")
def query_ai(request: QueryRequest):
    """
    Validated question-answer endpoint.

    1. User input is validated (before any model call).
    2. The first AI model generates an answer.
    3. The raw answer is validated.
    4. A second AI model reviews and improves the answer.
    5. The final answer is returned to the user.
    """
    validate_user_input(request.question)

    if not client:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY not configured")

    try:
        primary_response = client.models.generate_content(
            model=MODEL, contents=request.question
        )
        raw_answer = primary_response.text or ""

        validate_model_output(raw_answer)

        reviewed_answer = review_model_output(raw_answer)

        return {
            "question": request.question,
            "answer": reviewed_answer,
        }
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
