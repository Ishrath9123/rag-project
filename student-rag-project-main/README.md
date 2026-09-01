# RAG Learning App

A Retrieval-Augmented Generation (RAG) application built with Python, ChromaDB, SentenceTransformers, and Google Gemini. You'll build this incrementally over Weeks 10–15.

## What This App Does

You can ask this app questions about Python, machine learning, databases, APIs, and AI concepts. It finds the most relevant documents from its knowledge base and sends them to Gemini as context — so the answers are grounded in real information rather than guesswork.

## System Architecture

```
User Query
    │
    ▼
[security.py]      ← Validate and sanitize input (Week 12)
    │
    ▼
[compliance.py]    ← Tag metadata & redact sensitive data (Week 18)
    │
    ▼
[workflow.py]      ← Rewrite query for better retrieval (Week 15)
    │
    ▼
[embeddings.py]    ← Convert query to a vector
    │
    ▼
[vector_store.py]  ← Find similar document vectors in ChromaDB
    │
    ▼
[filters.py]       ← Remove irrelevant results (Week 14)
    │
    ▼
[rag_pipeline.py]  ← Build prompt with retrieved context
    │
    ▼
  Gemini API       ← Generate answer
    │
    ▼
[monitoring.py]    ← Check for hallucinations (Week 13)
    │
    ▼
[app.py]           ← Display answer, sources, confidence
```

## Setup

### 1. Clone the repository
```bash
git clone <repo-url>
cd student-rag-project
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

Activate it:
- **Mac/Linux:** `source venv/bin/activate`
- **Windows:** `venv\Scripts\activate`

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your Gemini API key

Copy the example environment file:
```bash
cp .env.example .env
```

Open `.env` and replace `your-gemini-api-key-here` with your actual key.
Get a free key at: https://aistudio.google.com/apikey

### 5. Run the app
```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

### 6. Run tests
```bash
pytest
```

Run this from the `student-rag-project-main` folder. GitHub Actions also runs these tests on every push and pull request.

---

## File Descriptions

| File | Purpose |
|------|---------|
| `app.py` | Streamlit web interface |
| `config.py` | Configuration constants |
| `embeddings.py` | Convert text to vector embeddings |
| `vector_store.py` | Store and search vectors with ChromaDB |
| `data_loader.py` | Sample tech documents |
| `rag_pipeline.py` | Central orchestration — ties everything together |
| `conversation.py` | Conversation history (Week 11) |
| `security.py` | Input validation and security (Week 12) |
| `monitoring.py` | Hallucination detection (Week 13) |
| `filters.py` | Similarity filtering and fallbacks (Week 14) |
| `workflow.py` | Query rewriting and multi-hop retrieval (Week 15) |
| `compliance.py` | Metadata tagging and sensitive data redaction (Week 18) |
| `tests/test_basic.py` | Unit tests for redaction, tagging, and input safety (Week 19) |
| `.github/workflows/tests.yml` | GitHub Actions CI — runs pytest on push and pull request |

---

## Compliance & Data Protection (Week 18)

This app is a learning project, but we treat it as if it could handle real user data in production.

### Applicable trust principles

| Principle | Why it applies |
|-----------|----------------|
| **Security** | User queries are sent to an external LLM API (Gemini). We validate input at the boundary (`security.py`) and redact sensitive data before it leaves the app. |
| **Confidentiality** | Users might paste emails, phone numbers, or other PII into the chat. We tag and redact this data so it is not logged or stored in plain text. |
| **Privacy** | Conversation history is kept in session memory only. Sensitive fields are redacted before being saved to history or sent to the model. |

### Where sensitive data can appear

| Location | Examples | Handling |
|----------|----------|----------|
| **User input** | Names, emails, phone numbers, SSNs | Tagged as `user_input`, redacted before API calls and logging |
| **Stored documents** | Could include internal or proprietary text in a real deployment | Tagged as `document` with `public` sensitivity for our sample docs |
| **Model output** | May repeat or summarize sensitive input | Tagged as `model_output`, redacted before logging |
| **Logs / errors** | Could accidentally capture query text | `safe_log()` redacts before writing; error messages omit raw exception details |

### Metadata tags

Each piece of data gets three tags (defined in `compliance.py`):

- **sensitivity:** `public` / `internal` / `confidential` / `restricted`
- **data_type:** `PII` / `PHI` / `financial` / `operational`
- **source:** `user_input` / `document` / `model_output`

Tags are attached when documents are loaded into ChromaDB and when user queries and model responses are processed.

### Where redaction happens

1. **Before external API calls** — user queries are redacted before being sent to Gemini (rewrite + generate steps)
2. **Before logging** — `safe_log()` redacts emails, phones, SSNs, and credit card patterns
3. **Before saving conversation history** — redacted text is stored, not the raw sensitive input
4. **Before displaying errors** — error messages do not include raw exception text that might contain user data

### Limitations

- Pattern-based detection only (regex) — it will not catch all forms of sensitive data
- Redaction is for learning/demo purposes, not SOC 2 certification
- Session history is in-memory only and clears when the app restarts

---

## Testing (Week 19)

This project uses `pytest` for automated unit tests. The tests live in `tests/test_basic.py` and run both locally and in GitHub Actions.

### What we tested

- **Text redaction** — emails, phone numbers, SSNs, and credit card numbers are replaced with `[REDACTED]`
- **Metadata tagging** — documents and user input get the correct sensitivity, data type, and source tags
- **Input helpers** — `sanitize_input()` strips extra whitespace
- **Safety behavior** — prompt injection is blocked, and personal data is not returned in raw form

### Why these tests matter

Redaction and input validation are safety-critical. If they break, the app could log or send personal data, or let a prompt-injection attack through. These tests fail if that protection is removed.

### What is intentionally not tested

- Gemini API calls (query rewriting, answer generation, hallucination checks)
- ChromaDB / embedding search
- The Streamlit UI

Those steps need live APIs or a running app, so they are not part of this unit-test suite.

---

## Weekly Progress

- [x] Week 10 — Ran the starter app and explored the codebase
- [x] Week 11 — Implemented conversation context
- [x] Week 12 — Implemented input security
- [x] Week 13 — Implemented hallucination monitoring
- [x] Week 14 — Implemented filtering and fallbacks
- [x] Week 15 — Implemented multi-step AI workflows
- [x] Week 16 — Architecture diagram
- [x] Week 18 — Compliance (metadata tagging and redaction)
- [x] Week 19 — Testing and CI/CD foundations

---

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the high-level system diagram and component explanations.

![Architecture Diagram](docs/rag-app-architecture-diagram.png)

