# Week 4 — Starting the RAG Project

## Project Overview
This repository contains the baseline architecture for a Retrieval-Augmented Generation (RAG) system built using Python, FastAPI, and the Google Gemini API. The goal of this week's laboratory was to securely establish our backend server environment, manage environment configurations, and verify an active integration link to the generative AI model.

---

## File Structure & Purpose

* **`rag_app.py`**: The core backend file of the application. It initializes the FastAPI web framework instance and exposes a `/health` API endpoint. It is responsible for loading ecosystem configurations and initializing the connection wrapper to Google's `generativeai` package using our secret keys.
* **`.env`**: A local storage configuration file containing critical credentials, specifically the `GEMINI_API_KEY`. This ensures authentication variables are kept isolated from public source logic.
* **`.gitignore`**: A safety filter configuration instructing Git to intentionally skip tracking local runtime environments (`venv/`) and private credentials (`.env`). This guarantees our operational Gemini API keys remain completely confidential and are never uploaded to public online environments.
* **`requirements.txt`**: A standardized list specifying mandatory third-party software dependencies (such as `fastapi`, `uvicorn`, `python-dotenv`, and `google-generativeai`) required to run and maintain the server deployment uniformly across platforms.

---

## Project Verification Proof
The system has been comprehensively verified and functions locally as intended:
1. **API Lifecycle Verification**: Upon launching via the `uvicorn` engine, the server correctly fetches the key mapping from the system environment and logs:  
   `✅ Gemini API successfully connected!`
2. **Endpoint Evaluation**: Routing an HTTP browser query directly to `http://127.0.0.1:8000/health` successfully returns a clean web response parsing:  
   `{"status": "ok", "message": "RAG App is running!"}`

---

## Uncertainties and Reflections
The initial implementation went smoothly, though adjusting default Windows execution profiles from PowerShell to Command Prompt (`cmd`) was a key troubleshooting step required to get the virtual environment scripts to load without permission constraint interference. Moving forward, a major design consideration will be handling context sizes when structuring document chunk ingestion pipelines for the vector databases in upcoming modules.
