import json
import re
from datetime import datetime, timezone
from pathlib import Path

SESSIONS_DIR = Path(__file__).resolve().parent / "sessions"
SESSION_ID_PATTERN = re.compile(r"^[\w-]{1,64}$")
DEFAULT_SESSION_ID = "default"


def _sanitize_session_id(session_id: str | None) -> str:
    if not session_id or not SESSION_ID_PATTERN.fullmatch(session_id):
        return DEFAULT_SESSION_ID
    return session_id


def _auth_file(session_id: str) -> Path:
    return SESSIONS_DIR / f"{session_id}.auth.json"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _default_auth_state() -> dict:
    return {
        "verified": False,
        "message_count": 0,
        "lead": None,
        "otp_hash": None,
        "otp_expires_at": None,
        "lead_submitted_at": None,
        "verified_at": None,
    }


def load_auth_state(session_id: str | None = None) -> dict:
    safe_session_id = _sanitize_session_id(session_id)
    auth_file = _auth_file(safe_session_id)

    if not auth_file.exists():
        return _default_auth_state()

    return {**_default_auth_state(), **json.loads(auth_file.read_text(encoding="utf-8"))}


def save_auth_state(session_id: str | None, state: dict) -> None:
    safe_session_id = _sanitize_session_id(session_id)
    auth_file = _auth_file(safe_session_id)
    auth_file.parent.mkdir(parents=True, exist_ok=True)
    auth_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
