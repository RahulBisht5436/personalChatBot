import os

from streamingbackend.rag.config import get_repo_root

try:
    from dotenv import load_dotenv

    load_dotenv(get_repo_root() / ".env")
except ImportError:
    pass

FREE_CHAT_LIMIT = int(os.getenv("FREE_CHAT_LIMIT", "5"))
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))
LEAD_NOTIFICATION_EMAIL = os.getenv("LEAD_NOTIFICATION_EMAIL", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}
