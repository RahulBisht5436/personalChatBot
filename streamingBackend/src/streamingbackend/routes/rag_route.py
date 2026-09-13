from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from streamingbackend.rag.ingest_service import get_ingest_status, ingest_documents
from streamingbackend.rag.resources_service import resolve_document_path

rag_router = APIRouter(
    prefix="/rag",
    tags=["rag"],
)


@rag_router.get("/health")
async def health():
    return {"message": "RAG route is healthy"}


@rag_router.get("/status")
async def status():
    return get_ingest_status()


@rag_router.post("/ingest")
async def ingest(force: bool = Query(default=False)):
    return ingest_documents(force=force)


@rag_router.get("/files/{file_name:path}")
async def download_file(file_name: str):
    file_path = resolve_document_path(file_name)
    if file_path is None:
        raise HTTPException(status_code=404, detail="File not found.")

    media_type = "application/octet-stream"
    if file_path.suffix.lower() == ".pdf":
        media_type = "application/pdf"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=file_path.name,
    )
