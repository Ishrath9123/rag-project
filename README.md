# Week 7 — Validating User Input and AI Output

## Project Overview

This repository extends the Week 6 multi-step backend with **basic safety checks** at two important points: before user input is sent to the AI model, and before the AI's response is returned to the user. It also adds a **second AI model call** whose job is to review and improve the output of the first model.

---

## Week 7 — Validation and Review

### New endpoint: `POST /query`

The new endpoint accepts a JSON body with a `question` field (defined by the `QueryRequest` Pydantic model) and runs this pipeline:

1. **User input is validated** — `validate_user_input()` rejects empty, too-short (< 5 chars), or too-long (> 500 chars) questions with a clear `400` error. The AI model is never called when input validation fails.
2. **The first AI model generates an answer** from the user's question.
3. **The raw answer is validated** — `validate_model_output()` rejects empty or suspiciously short responses with a `500` error.
4. **A second AI model reviews the answer** — `review_model_output()` asks Gemini to improve the response if it is unclear or incomplete, and return it unchanged if it is already good.
5. **The final (reviewed) answer is returned** to the user.

### Why input validation exists

Users can send empty, broken, or malicious input. Rejecting bad input early returns a clear error message immediately, avoids wasting API calls (and quota) on garbage requests, and protects the model from inputs it can't answer meaningfully.

### Why output validation exists

AI models can hallucinate or return empty, incomplete, or confusing answers. Checking the raw response before returning it ensures we never send obviously bad output to users — a controlled `500` error is better than a blank answer.

### Why a second AI model reviews responses

Instead of trusting the first model's answer blindly, a second model call acts as a quality gate: it checks and improves the answer before the user sees it. This "one model checks another" pattern is commonly used in production GenAI systems to make outputs more reliable.

---

## File Structure & Purpose

| File | Purpose |
|------|---------|
| **`rag_app.py`** | FastAPI backend with `/health`, `/test-gemini`, `/chat/`, and `/query` endpoints |
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
6. **`/query`** (Week 7) validates input, generates an answer, validates the output, and has a second model review it before returning.

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
| Validated query (Week 7) | `POST` http://127.0.0.1:8000/query with `{"question": "What is retrieval augmented generation?"}` | JSON with `question` and the reviewed `answer` |
| Invalid input (Week 7) | `POST /query` with `{"question": ""}` or `{"question": "hi"}` | `400` with `"Question cannot be empty"` / `"Question is too short"` — no AI call is made |

The easiest way to test `POST /query` is the automatic docs page: open http://127.0.0.1:8000/docs, expand **POST /query**, click **Try it out**, enter a request body, and click **Execute**.

On startup, the terminal should print: `Gemini API successfully connected!`

---

## Learning Outcomes (Week 7)

- Defined request shapes with Pydantic (`QueryRequest`) so FastAPI validates the JSON body automatically
- Rejected bad user input early with clear `400` errors, before any AI call is made
- Validated AI output before returning it, so users never see empty or broken responses
- Used a second AI model call to review and improve the first model's answer
- Returned controlled, readable error messages for every failure case

---

## Reflections

The main challenge this week was making the review step return only the improved answer — the reviewer initially replied with commentary like "this response is already good" instead of the answer itself, which was fixed by tightening the review prompt. Free-tier rate limits are also more noticeable now that a single `/query` request makes two model calls; transient `503 high demand` errors from Gemini resolve on retry. Next steps will add retrieval (RAG) in front of this validated pipeline.
