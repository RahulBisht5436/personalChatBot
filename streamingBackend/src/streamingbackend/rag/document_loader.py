import base64
import mimetypes
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from streamingbackend.rag.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    SUPPORTED_EXTENSIONS,
    get_repo_root,
)

TEXT_EXTENSIONS = {".txt", ".md", ".csv"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

VISION_EXTRACTION_PROMPT = (
    "Extract all readable text from this image. "
    "If it is a certificate, degree, resume, or project screenshot, "
    "include names, dates, institutions, skills, and achievements."
)


def _load_env() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(get_repo_root() / ".env")
    except ImportError:
        pass


def _extract_text_with_vision(image_bytes: bytes, mime_type: str) -> str:
    from openai import OpenAI

    _load_env()
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": VISION_EXTRACTION_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{encoded}",
                        },
                    },
                ],
            }
        ],
    )
    return (response.choices[0].message.content or "").strip()


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def _read_pdf_with_vision_ocr(path: Path) -> str:
    import pymupdf

    page_texts: list[str] = []
    with pymupdf.open(path) as document:
        for page in document:
            pixmap = page.get_pixmap(dpi=180)
            page_text = _extract_text_with_vision(pixmap.tobytes("png"), "image/png")
            if page_text:
                page_texts.append(page_text)

    return "\n\n".join(page_texts).strip()


def _read_pdf_file(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages).strip()
    if text:
        return text

    return _read_pdf_with_vision_ocr(path)


def _read_image_file(path: Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    return _extract_text_with_vision(path.read_bytes(), mime_type)


def load_document_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        return _read_text_file(path)
    if suffix == ".pdf":
        return _read_pdf_file(path)
    if suffix in IMAGE_EXTENSIONS:
        return _read_image_file(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def discover_documents(documents_path: Path) -> list[Path]:
    if not documents_path.exists():
        return []

    files: list[Path] = []
    for path in documents_path.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(path)
    return sorted(files)


def split_documents(path: Path, text: str, doc_id: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    metadata = {
        "source": str(path),
        "doc_id": doc_id,
        "file_name": path.name,
    }
    return splitter.create_documents([text], metadatas=[metadata])
