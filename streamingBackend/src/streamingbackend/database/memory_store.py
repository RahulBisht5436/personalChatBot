import json
import re
from pathlib import Path

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

SESSIONS_DIR = Path(__file__).resolve().parent / "sessions"
DEFAULT_SESSION_ID = "default"
SESSION_ID_PATTERN = re.compile(r"^[\w-]{1,64}$")


def _sanitize_session_id(session_id: str | None) -> str:
    if not session_id or not SESSION_ID_PATTERN.fullmatch(session_id):
        return DEFAULT_SESSION_ID
    return session_id


def _memory_file(session_id: str) -> Path:
    return SESSIONS_DIR / f"{session_id}.json"


def _serialize_message(message: BaseMessage) -> dict[str, str]:
    if isinstance(message, HumanMessage):
        role = "human"
    elif isinstance(message, AIMessage):
        role = "ai"
    else:
        role = message.type

    return {"role": role, "content": str(message.content)}


def _deserialize_message(data: dict[str, str]) -> BaseMessage:
    role = data.get("role", "human")
    content = data.get("content", "")

    if role == "human":
        return HumanMessage(content=content)
    if role == "ai":
        return AIMessage(content=content)

    return HumanMessage(content=content)


def load_chat_history(session_id: str | None = None) -> list[BaseMessage]:
    safe_session_id = _sanitize_session_id(session_id)
    memory_file = _memory_file(safe_session_id)

    if not memory_file.exists() or memory_file.stat().st_size == 0:
        return []

    raw = memory_file.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    data = json.loads(raw)
    return [_deserialize_message(item) for item in data]


def save_chat_history(
    chat_history: list[BaseMessage], session_id: str | None = None
) -> None:
    safe_session_id = _sanitize_session_id(session_id)
    memory_file = _memory_file(safe_session_id)
    memory_file.parent.mkdir(parents=True, exist_ok=True)
    payload = [_serialize_message(message) for message in chat_history]
    memory_file.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
