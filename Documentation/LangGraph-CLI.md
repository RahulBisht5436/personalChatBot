# LangGraph CLI — Inside This Project

You **do not** need `langgraph new` — this repo already has a LangGraph app. The CLI is wired to your existing graph.

---

## Two ways to run the backend

| Mode | Command | Port | Purpose |
|------|---------|------|---------|
| **Production app** | `uv run serve` | `8000` | FastAPI + chat widget + OTP + RAG routes |
| **LangGraph dev** | `uv run langgraph-dev` | `2024` | Graph debugging in **LangGraph Studio** |

Use **FastAPI** for the full portfolio chatbot. Use **LangGraph dev** only when you want to visualize and test the graph in Studio.

---

## Setup (one time)

### 1. Install dependencies

```powershell
cd streamingBackend
uv sync
```

`langgraph-cli[inmem]` is already in `pyproject.toml`.

> **Python version:** Use **3.12** for the backend (see `streamingBackend/.python-version`).
> `langgraph-cli[inmem]` does not install cleanly on Python 3.14 on Windows yet.

### 2. Configure `.env`

At repo root (`personalChatBot/.env`):

```env
OPENAI_API_KEY=sk-...

# Optional — enables tracing in LangGraph Studio
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=personal-chatbot
```

Get a LangSmith key: https://smith.langchain.com/settings

### 3. Ingest RAG (if testing retrieval)

```powershell
uv run ingest-rag
```

---

## Launch LangGraph dev server

```powershell
cd streamingBackend
uv run langgraph-dev
```

Or directly:

```powershell
cd streamingBackend
uv run langgraph dev
```

This starts:

- **Agent server:** http://127.0.0.1:2024
- **LangGraph Studio:** opens in browser (or go to https://smith.langchain.com/studio)

---

## Project layout (what maps to the official docs)

Official docs say to run `langgraph new`. In this project, the equivalent files already exist:

| Official template | This project |
|-------------------|--------------|
| `langgraph new ...` | Not needed |
| `langgraph.json` | `streamingBackend/langgraph.json` |
| Graph export | `streamingBackend/src/streamingbackend/graph.py` → `graph` |
| `pip install -e .` | `uv sync` in `streamingBackend/` |
| `.env` | `personalChatBot/.env` (repo root) |

### `langgraph.json`

```json
{
  "dependencies": ["."],
  "graphs": {
    "portfolio_chatbot": "./src/streamingbackend/graph.py:graph"
  },
  "env": "../.env"
}
```

### Graph flow

```
START → retrieve_context → chatbot_interaction → END
```

Defined in `graph.py`, nodes in:

- `services/retrieve_node.py` — RAG retrieval
- `services/chatbot_node.py` — LLM reply

---

## Test input in LangGraph Studio

Use this state when invoking the graph:

```json
{
  "user_message": "What is your degree and institute?",
  "chat_history": [],
  "retrieved_context": null,
  "response": null
}
```

Studio runs the graph directly — it does **not** go through FastAPI auth or session storage.

---

## How FastAPI uses the same graph

`chatbot_service.py` imports the same compiled graph:

```python
from streamingbackend.graph import graph as compiled_graph

result = compiled_graph.invoke({...})
```

FastAPI adds on top:

- Session history (`memory_store.py`)
- OTP / lead verification
- HTTP routes for the Next.js widget

---

## Common commands

```powershell
# Full app (widget + API)
cd streamingBackend
uv run serve

# Graph dev server (Studio only)
cd streamingBackend
uv run langgraph-dev

# RAG ingest
uv run ingest-rag
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named langgraph_cli` | Run `uv sync` in `streamingBackend` (installs `langgraph-cli[inmem]`) |
| `langgraph: command not found` | Run via `uv run langgraph-dev` or `uv run langgraph dev` |
| `jsonschema-rs` / Rust build error | Switch to Python 3.12: `streamingBackend/.python-version` |
| Graph fails to load | Run from `streamingBackend/` where `langgraph.json` lives |
| RAG returns empty context | Run `uv run ingest-rag` and check `RAGDatabase/documents/` |
| No traces in Studio | Set `LANGSMITH_API_KEY` and `LANGSMITH_TRACING=true` in `.env` |
| Port 2024 in use | `uv run langgraph dev --port 2025` |

---

## Do you need both servers?

- **Developing the widget / OTP / embed** → `uv run serve` + frontend `npm run dev`
- **Debugging graph nodes / prompts / RAG** → `uv run langgraph-dev`

They can run at the same time on different ports.
