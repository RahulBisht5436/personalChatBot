import os
from pathlib import Path

COLLECTION_NAME = "rahul_career_knowledge"
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".csv"}
CHUNK_SIZE = 900
CHUNK_OVERLAP = 120
TOP_K = 4


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def get_rag_database_path() -> Path:
    configured = os.getenv("RAG_DATABASE_PATH")
    if configured:
        return Path(configured).resolve()
    return get_repo_root() / "RAGDatabase"


def get_documents_path() -> Path:
    return get_rag_database_path() / "documents"


def get_chroma_path() -> Path:
    return get_rag_database_path() / "chroma"


def get_manifest_path() -> Path:
    return get_rag_database_path() / "manifest.json"
