# Personal Chatbot (Streaming)

Portfolio chatbot with LangGraph backend, Next.js widget, RAG, and email verification.

## Structure

```
Streaming/
├── streamingBackend/     # FastAPI + LangGraph + RAG
├── streamingFrontend/    # Next.js embeddable chat widget
├── RAGDatabase.example/  # Sample config — copy to ../RAGDatabase locally
└── .env.example          # Copy to repo root .env (see below)
```

## Setup

1. Copy `.env.example` to the repo root `.env` and fill in secrets.
2. Create `../RAGDatabase/documents/` locally and add your career files (not committed).
3. Copy `RAGDatabase.example/resources.json` to `../RAGDatabase/resources.json` and customize links.
4. Backend:

```powershell
cd streamingBackend
uv sync
uv run ingest-rag
uv run serve
```

5. Frontend:

```powershell
cd streamingFrontend/chatbot_frontend
npm install
npm run dev
```

## Security

Do not commit:

- `.env` files
- PDFs, resumes, certificates in `RAGDatabase/documents/`
- `database/sessions/*.json` (chat + lead data)
- Chroma vector store (`RAGDatabase/chroma/`)

These paths are listed in `.gitignore`.
