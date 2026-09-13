from langchain_chroma import Chroma

from streamingbackend.rag.config import COLLECTION_NAME, get_chroma_path
from streamingbackend.utility.llm_models.openai_embeddings import embeddings


def get_vector_store() -> Chroma:
    chroma_path = get_chroma_path()
    chroma_path.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(chroma_path),
    )


def delete_document_chunks(doc_id: str) -> int:
    store = get_vector_store()
    existing = store.get(where={"doc_id": doc_id})
    ids = existing.get("ids") or []
    if ids:
        store.delete(ids=ids)
    return len(ids)


def get_collection_stats() -> dict:
    store = get_vector_store()
    data = store.get(include=["metadatas"])
    ids = data.get("ids") or []
    metadatas = data.get("metadatas") or []
    doc_ids = {meta.get("doc_id") for meta in metadatas if meta and meta.get("doc_id")}
    return {
        "chunk_count": len(ids),
        "document_count": len(doc_ids),
    }
