import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from streamingbackend.rag.config import get_documents_path, get_manifest_path
from streamingbackend.rag.document_loader import (
    discover_documents,
    load_document_text,
    split_documents,
)
from streamingbackend.rag.rag_store import delete_document_chunks, get_vector_store


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _relative_doc_path(path: Path, documents_path: Path) -> str:
    return path.relative_to(documents_path).as_posix()


def _load_manifest(manifest_path: Path) -> dict:
    if not manifest_path.exists():
        return {"files": {}, "last_run": None}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _save_manifest(manifest_path: Path, manifest: dict) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def ingest_documents(force: bool = False) -> dict:
    documents_path = get_documents_path()
    manifest_path = get_manifest_path()
    documents_path.mkdir(parents=True, exist_ok=True)

    manifest = _load_manifest(manifest_path)
    tracked_files: dict = manifest.setdefault("files", {})
    store = get_vector_store()

    discovered = discover_documents(documents_path)
    discovered_keys = {_relative_doc_path(path, documents_path) for path in discovered}

    removed_files: list[str] = []
    for tracked_key in list(tracked_files.keys()):
        if tracked_key not in discovered_keys:
            delete_document_chunks(tracked_files[tracked_key]["doc_id"])
            removed_files.append(tracked_key)
            del tracked_files[tracked_key]

    ingested: list[str] = []
    skipped: list[str] = []
    failed: list[dict[str, str]] = []

    for path in discovered:
        relative_key = _relative_doc_path(path, documents_path)
        current_hash = _file_hash(path)
        previous = tracked_files.get(relative_key)

        if (
            not force
            and previous
            and previous.get("hash") == current_hash
        ):
            skipped.append(relative_key)
            continue

        doc_id = previous["doc_id"] if previous else relative_key
        try:
            if previous:
                delete_document_chunks(doc_id)

            text = load_document_text(path)
            if not text:
                failed.append(
                    {
                        "file": relative_key,
                        "error": "No readable text extracted from document.",
                    }
                )
                continue

            chunks = split_documents(path, text, doc_id)
            store.add_documents(chunks)

            tracked_files[relative_key] = {
                "doc_id": doc_id,
                "hash": current_hash,
                "size": path.stat().st_size,
                "chunk_count": len(chunks),
                "ingested_at": _utc_now(),
            }
            ingested.append(relative_key)
        except Exception as error:
            failed.append({"file": relative_key, "error": str(error)})

    manifest["last_run"] = _utc_now()
    _save_manifest(manifest_path, manifest)

    return {
        "ingested": ingested,
        "skipped": skipped,
        "removed": removed_files,
        "failed": failed,
        "totals": {
            "discovered": len(discovered),
            "ingested": len(ingested),
            "skipped": len(skipped),
            "removed": len(removed_files),
            "failed": len(failed),
        },
        "last_run": manifest["last_run"],
    }


def get_ingest_status() -> dict:
    manifest = _load_manifest(get_manifest_path())
    from streamingbackend.rag.rag_store import get_collection_stats

    stats = get_collection_stats()
    files = manifest.get("files", {})
    return {
        "documents_path": str(get_documents_path()),
        "manifest_path": str(get_manifest_path()),
        "last_run": manifest.get("last_run"),
        "tracked_files": files,
        "collection": stats,
    }
