import json
import os
from pathlib import Path

import logfire
from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from streamingbackend.routes.chatbot_route import chatbot_router
from streamingbackend.routes.rag_route import rag_router


def _load_logfire_token() -> str | None:
    backend_root = Path(__file__).resolve().parents[2]
    creds_path = backend_root / ".logfire" / "logfire_credentials.json"
    if not creds_path.is_file():
        return None
    return json.loads(creds_path.read_text(encoding="utf-8")).get("token")


os.environ.setdefault("LANGSMITH_TRACING", "true")
os.environ.setdefault("LANGSMITH_OTEL_ENABLED", "true")
os.environ.setdefault("LANGSMITH_OTEL_ONLY", "true")

logfire.configure(
    token=_load_logfire_token(),
    service_name="streaming-backend",
    service_version="1.0.0",
    environment="dev",
    send_to_logfire="if-token-present",
)

app = FastAPI(
    title="Streaming Backend",
    description="A backend for streaming data in langgraph and fastapi",
    version="1.0.0",
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logfire.info("Streaming Backend is running")

@app.get("/")
def read_root():
    # this return the status of health and general information about the backend
    return {
        "status": "healthy",
        "message": "Streaming Backend is running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
    }
    
app.include_router(chatbot_router)
app.include_router(rag_router)

logfire.instrument_fastapi(app)
logfire.instrument_httpx()
logfire.instrument_openai()