import json
import os
from pathlib import Path
from urllib.parse import quote

from streamingbackend.rag.config import get_rag_database_path


def get_resources_path() -> Path:
    return get_rag_database_path() / "resources.json"


def get_api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def _load_resources() -> dict:
    resources_path = get_resources_path()
    if not resources_path.exists():
        return {"downloads": [], "projects": [], "profiles": []}
    return json.loads(resources_path.read_text(encoding="utf-8"))


def _matches_keywords(query: str, keywords: list[str]) -> bool:
    normalized = query.lower()
    return any(keyword.lower() in normalized for keyword in keywords)


def _build_download_url(file_name: str) -> str:
    encoded_name = quote(file_name)
    return f"{get_api_base_url()}/rag/files/{encoded_name}"


def match_resources(query: str) -> dict:
    resources = _load_resources()
    normalized = query.lower()

    downloads = [
        item
        for item in resources.get("downloads", [])
        if _matches_keywords(normalized, item.get("keywords", []))
    ]

    projects = [
        item
        for item in resources.get("projects", [])
        if _matches_keywords(normalized, item.get("keywords", []))
    ]
    if any(word in normalized for word in ("project", "projects", "portfolio work")):
        projects = resources.get("projects", [])

    profiles = [
        item
        for item in resources.get("profiles", [])
        if _matches_keywords(normalized, item.get("keywords", []))
    ]

    return {
        "downloads": downloads,
        "projects": projects,
        "profiles": profiles,
    }


def format_resource_context(query: str) -> str:
    matched = match_resources(query)
    sections: list[str] = []

    if matched["downloads"]:
        lines = []
        for item in matched["downloads"]:
            file_name = item["file_name"]
            label = item.get("label", file_name)
            url = _build_download_url(file_name)
            lines.append(f"- [{label}]({url})")
        sections.append(
            "Downloadable files (include these markdown links when the visitor asks for files):\n"
            + "\n".join(lines)
        )

    if matched["projects"]:
        lines = []
        for item in matched["projects"]:
            url = item.get("url", "").strip()
            if not url:
                continue
            name = item["name"]
            description = item.get("description", "")
            lines.append(f"- [{name}]({url}) — {description}".strip())
        if lines:
            sections.append(
                "Project links (include these markdown links when the visitor asks about projects):\n"
                + "\n".join(lines)
            )

    if matched["profiles"]:
        lines = []
        for item in matched["profiles"]:
            url = item.get("url", "").strip()
            if not url:
                continue
            lines.append(f"- [{item['name']}]({url})")
        sections.append(
            "Profile links:\n" + "\n".join(lines)
        )

    return "\n\n".join(sections)


def resolve_document_path(file_name: str) -> Path | None:
    from streamingbackend.rag.config import get_documents_path

    documents_path = get_documents_path().resolve()
    candidate = (documents_path / file_name).resolve()

    if not str(candidate).startswith(str(documents_path)):
        return None
    if not candidate.exists() or not candidate.is_file():
        return None
    return candidate
