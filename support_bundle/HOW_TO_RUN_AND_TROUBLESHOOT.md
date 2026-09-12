# AtlasIQ Run And Troubleshoot Guide

This file explains the correct setup and the most common reason for `Query failed`.

## 1. What must be true before asking questions

- The app server is running.
- The `.env` file exists in the project root.
- `ENABLE_LANGCHAIN_RUNTIME=true`
- `OPENAI_API_KEY=` contains a valid OpenAI API key.
- You restarted the server after editing `.env`.
- You indexed documents first by clicking `Index Seed Docs` or uploading/pasting knowledge.

## 2. Correct `.env` values

Example:

```env
ENABLE_LANGCHAIN_RUNTIME=true
OPENAI_API_KEY=sk-proj-your-real-key-here
OPENAI_CHAT_MODEL=gpt-4o-mini
```

## 3. Start the app

From the project folder:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.api.main:app --reload
```

Then open:

```text
http://localhost:8000
```

## 4. If the site opens but `Query failed` appears

This usually means:

- the OpenAI API key is invalid
- the OpenAI key was exposed and revoked
- billing or project access is missing
- the selected model is not available to that key
- the network request to OpenAI failed

## 5. What the app now does

If LangChain crashes during answer generation, AtlasIQ now falls back to deterministic grounded output instead of failing the whole request.

That means:

- the answer should still appear
- citations should still appear
- the strategy may switch to `deterministic`
- a note will explain that the LangChain request failed

## 6. Best first test question

After clicking `Index Seed Docs`, try:

```text
What is our P1 incident communication SLA?
```

## 7. Important security step

If you pasted or exposed your OpenAI API key anywhere in chats, screenshots, or code, rotate it immediately in the OpenAI dashboard and replace it in `.env`.
