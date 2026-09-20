import re

from presidio_analyzer import AnalyzerEngine

ALLOWED_CONTACTS = {
    "hireRahulbisht@gmail.com",
    "7982669162",
}

OUTPUT_PII_ENTITIES = [
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CREDIT_CARD",
    "US_SSN",
    "US_BANK_NUMBER",
]

_analyzer = AnalyzerEngine()


def _normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", value)


def _is_allowed(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in ALLOWED_CONTACTS:
        return True
    if _normalize_phone(value) == _normalize_phone("7982669162"):
        return True
    return False


def mask_email(email: str) -> str:
    """shikhar@gmail.com -> shik****@**.com"""
    local, sep, domain = email.partition("@")
    if not sep or not domain:
        return "****@**.***"

    visible = local[:4] if len(local) >= 4 else local[:1]
    name_part = f"{visible}****"

    tld = domain.rsplit(".", 1)[-1]
    return f"{name_part}@**.{tld}"


def mask_phone(phone: str) -> str:
    """7982669162 -> ******9162"""
    digits = _normalize_phone(phone)
    if len(digits) <= 4:
        return "*" * len(digits)
    hidden = "*" * (len(digits) - 4)
    return f"{hidden}{digits[-4:]}"


def mask_default(value: str) -> str:
    """Cards / SSN / bank numbers: fully hidden."""
    return "*" * len(value)


def _mask_entity(entity_type: str, original: str) -> str:
    if entity_type == "EMAIL_ADDRESS":
        return mask_email(original)
    if entity_type == "PHONE_NUMBER":
        return mask_phone(original)
    return mask_default(original)


def sanitize_assistant_reply(text: str) -> str:
    if not text or not text.strip():
        return text

    results = _analyzer.analyze(
        text=text,
        entities=OUTPUT_PII_ENTITIES,
        language="en",
    )

    # Replace from end → start so indexes stay valid
    for match in sorted(results, key=lambda r: r.start, reverse=True):
        original = text[match.start : match.end]
        if _is_allowed(original):
            continue
        masked = _mask_entity(match.entity_type, original)
        text = text[: match.start] + masked + text[match.end :]

    return text