from guardrails import Guard
from guardrails.errors import ValidationError
from guardrails_ai.toxic_language import ToxicLanguage

# Local model — no API key
_output_toxic_guard = Guard().use(
    ToxicLanguage(
        use_local=True,
        threshold=0.5,              # 0.0–1.0; raise to 0.7 if too many false positives
        validation_method="sentence",  # check sentence-by-sentence
        on_fail="fix",               # strip toxic lines from bot reply
    )
)

_input_toxic_guard = Guard().use(
    ToxicLanguage(
        use_local=True,
        threshold=0.5,
        validation_method="full",    # whole user message
        on_fail="noop",              # caller checks validation_passed
    )
)

SAFE_BLOCKED_INPUT = (
    "Please keep the conversation respectful. "
    "I’m here to help with Rahul’s portfolio, skills, and career details."
)

SAFE_BLOCKED_OUTPUT = (
    "I’m not able to share that response. "
    "Ask me about Rahul’s experience, projects, or resume instead."
)


def sanitize_toxic_output(text: str) -> tuple[str, bool]:
    """Returns (sanitized_text, was_modified)."""
    if not text or not text.strip():
        return text, False

    outcome = _output_toxic_guard.validate(text)
    sanitized = outcome.validated_output or text
    return sanitized, sanitized != text


def is_toxic_input(text: str) -> bool:
    if not text or not text.strip():
        return False

    try:
        outcome = _input_toxic_guard.validate(text)
    except ValidationError:
        return True

    return not outcome.validation_passed