# Week 6 — Multi-Step Execution

## Project Overview

This repository extends the Week 5 Gemini integration with **multi-step execution**. Instead of a single prompt-and-response call, the backend runs two sequential Gemini steps server-side: first an outline, then a full answer built from that outline. The final response depends on the earlier step's output.

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
3. **`test_gemini()`** runs a two-step flow: outline generation, then expansion into a final answer.
4. **`/test-gemini`** exposes that function as an HTTP endpoint for easy browser testing.
5. **`/chat/`** reuses the same multi-step logic but accepts a custom prompt from the user.

---

## Multi-Step Flow

The Gemini logic lives in `test_gemini()`. Both `/test-gemini` and `/chat/` call this function, so the multi-step behavior is shared.

| Step | Responsibility | Input | Output |
|------|----------------|-------|--------|
| **1 — Outline** | Break the question into 3–5 bullet points | User's question | Short outline (logged to the server terminal, not returned to the client) |
| **2 — Expand** | Write a complete answer guided by the outline | User's question + Step 1 outline | Final answer returned in the API response |

### Why the steps are separated

- **Step 1** forces the model to plan before writing, which tends to produce more structured answers.
- **Step 2** expands that plan into prose, so the final output clearly depends on the earlier AI call.
- Keeping both steps server-side gives us control over the sequence without changing the Week 5 API shape.

This pattern is a foundation for later work (RAG, validation, guardrails) where multiple logical steps run in order.

---

## `test_gemini()` — Logic Explanation

```python
def test_gemini(prompt: str = "Explain how photosynthesis works in simple terms.") -> dict:
    if not client:
        raise ValueError("GEMINI_API_KEY not configured")

    outline_prompt = (
        f"Generate a short bullet-point outline (3-5 points) for answering: {prompt}"
    )
    outline_response = client.models.generate_content(model=MODEL, contents=outline_prompt)
    outline = outline_response.text

    expand_prompt = (
        f"Using this outline:\n{outline}\n\n"
        f"Write a clear, complete answer to: {prompt}"
    )
    final_response = client.models.generate_content(model=MODEL, contents=expand_prompt)

    return {"model": MODEL, "prompt": prompt, "answer": final_response.text}
```

### Step-by-step logic

1. **Environment setup (at startup)** — Before `test_gemini()` runs, `load_dotenv()` loads `GEMINI_API_KEY` from `.env`, and `genai.Client()` is created.

2. **Guard check** — `if not client` verifies the API key exists before any Gemini calls.

3. **Step 1 — Outline** — Send a prompt asking Gemini for a short bullet-point outline for the user's question. Store the result in `outline` and log it to the terminal for inspection.

4. **Step 2 — Expand** — Build a second prompt that includes the outline from Step 1 and ask Gemini to write the full answer. Only this final text is returned to the client.

5. **Error handling (in endpoints)** — `/test-gemini` and `/chat/` catch API errors and return clear HTTP status codes instead of exposing secrets or crashing the server.

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
| Gemini integration | http://127.0.0.1:8000/test-gemini | JSON with `status`, `model`, `prompt`, and final `answer` (two Gemini calls; outline logged in terminal) |
| Custom prompt | http://127.0.0.1:8000/chat/?prompt=What+is+gravity | JSON with your question and the expanded answer |

On startup, the terminal should print: `Gemini API successfully connected!`

---

## Learning Outcomes (Week 6)

- Understood multi-step execution: later AI steps depend on earlier outputs
- Implemented a two-step outline-then-expand flow inside `test_gemini()`
- Kept API structure unchanged from Week 5 while moving control flow server-side
- Logged intermediate results for debugging without exposing them in the HTTP response
- Handled API errors with appropriate HTTP responses

---

## Reflections

The main challenge was keeping the flow simple while making the dependency between steps obvious — passing the Step 1 outline directly into the Step 2 prompt makes that link clear. Rate limits on the free tier mean each request now uses two API calls instead of one, so testing incrementally (confirm Step 1 logs an outline before relying on Step 2) helped catch issues early. Next steps for the RAG pipeline will add retrieval before the multi-step generation flow.
