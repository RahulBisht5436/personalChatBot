# Streaming Backend

## Run locally

From this directory:

```powershell
uv sync --package streamingbackend
uv run serve
```

Do **not** run bare `uvicorn` — it uses global Python and will fail with `ModuleNotFoundError`.

Alternative:

```powershell
uv run uvicorn streamingbackend.main:app --reload
```

## RAG (career knowledge)

1. Add PDFs, images, or text files to `../RAGDatabase/documents/`
2. Ingest into Chroma:

```powershell
uv run ingest-rag
```

3. Check status: `GET http://127.0.0.1:8000/rag/status`
4. Chat answers use retrieved context automatically via `POST /chatbot/`

See the main [README](../README.md#rag--ingest--search) for full details.

## Visitor verification (5 free messages)

After `FREE_CHAT_LIMIT` messages (default 5), visitors must submit:

- Name
- Email
- Company
- Designation they are looking for

An OTP is emailed to the visitor. After OTP verification, chat unlocks and the lead details are emailed to `LEAD_NOTIFICATION_EMAIL`.

Configure SMTP and lead email in the repo root `.env` (see `.env.example`).

Endpoints:

- `GET /chatbot/access?session_id=...`
- `POST /chatbot/lead`
- `POST /chatbot/verify-otp`
