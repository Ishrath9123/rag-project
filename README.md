# Week 5 — Gemini API Integration

## Project Overview

This repository extends the Week 4 RAG backend with a working **Google Gemini API** integration. The goal of this lab was to securely load an API key from the environment, connect to Gemini, send a test prompt, and verify that the model returns a generated response through our FastAPI server.

---

## File Structure & Purpose

| File | Purpose |
|------|---------|
| **`rag_app.py`** | FastAPI backend with `/health`, `/test-gemini`, and `/chat/` endpoints |
| **`.env`** | Stores `GEMINI_API_KEY` locally (never committed to GitHub) |
| **`.gitignore`** | Prevents Git from tracking `.env`, `venv/`, and cache files |
| **`requirements.txt`** | Python dependencies: `fastapi`, `uvicorn`, `python-dotenv`, `google-genai` |
| **`pyrightconfig.json`** / **`.vscode/settings.json`** | Editor config so the linter finds packages in `venv/` |

---

## Implementation Summary

1. **`load_dotenv()`** reads secrets from `.env` when the server starts.
2. **`genai.Client(api_key=...)`** authenticates with Google's Gemini API.
3. **`test_gemini()`** sends a default test prompt to the model and returns the answer.
4. **`/test-gemini`** exposes that function as an HTTP endpoint for easy browser testing.
5. **`/chat/`** reuses the same logic but accepts a custom prompt from the user.

---

## `test_gemini()` — Logic Explanation

The `test_gemini()` function is the core verification step for this lab. It proves that our backend can talk to Gemini end-to-end.

```python
def test_gemini(prompt: str = "Hello! Please respond in one short sentence.") -> dict:
    if not client:
        raise ValueError("GEMINI_API_KEY not configured")

    response = client.models.generate_content(model=MODEL, contents=prompt)
    return {"model": MODEL, "prompt": prompt, "answer": response.text}
```

### Step-by-step logic

1. **Environment setup (at startup)** — Before `test_gemini()` runs, `load_dotenv()` loads `GEMINI_API_KEY` from `.env`, and `genai.Client()` is created. This keeps secrets out of source code.

2. **Guard check** — `if not client` verifies the API key exists. If missing, we raise an error immediately instead of calling Google with invalid credentials.

3. **Model selection** — `MODEL` defaults to `gemini-2.5-flash` (override with `GEMINI_MODEL` in `.env`). This tells Gemini which model generates the text.

4. **API call** — `client.models.generate_content(model=MODEL, contents=prompt)` sends the prompt to Google and waits for a response.

5. **Return result** — We return a dictionary with the model name, the prompt we sent, and `response.text` (Gemini's answer). This confirms the full request–response cycle works.

6. **Error handling (in endpoints)** — `/test-gemini` and `/chat/` catch API errors (e.g. rate limits) and return clear HTTP status codes instead of crashing the server.

---

## How to Run

```powershell
cd rag-project
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file (not committed):

```
GEMINI_API_KEY=your_key_here
```

Start the server:

```powershell
python -m uvicorn rag_app:app --reload
```

---

## Verification Proof

| Test | URL | Expected result |
|------|-----|-----------------|
| Server health | http://127.0.0.1:8000/health | `{"status":"ok","message":"RAG App is running!"}` |
| Gemini integration | http://127.0.0.1:8000/test-gemini | JSON with `status`, `model`, `prompt`, and `answer` |
| Custom prompt | http://127.0.0.1:8000/chat/?prompt=Hello | JSON with your question and Gemini's answer |

On startup, the terminal should print: `Gemini API successfully connected!`

---

## Learning Outcomes (Week 5)

- Loaded API credentials securely using environment variables and `.gitignore`
- Initialized the Google Gemini client with the `google-genai` SDK
- Implemented `test_gemini()` to verify generative AI connectivity
- Exposed the integration through FastAPI endpoints for testing
- Handled API errors with appropriate HTTP responses

---

## Reflections

The main challenge was managing API rate limits on the free tier — switching from `gemini-2.0-flash` to `gemini-2.5-flash` resolved quota errors. Using a project virtual environment (`venv/`) also fixed editor import warnings. Next steps for the RAG pipeline will include document ingestion and vector search before sending context to Gemini.
