from pathlib import Path

from dotenv import load_dotenv
from nemoguardrails import RailsConfig

from streamingbackend.rag.config import get_repo_root
from streamingbackend.services.guardrails_logfire import LogfireRunnableRails

# NeMo creates OpenAI clients at import time; load .env first or guardrail
# self-check calls fail with 401 even when LangChain has the key.
load_dotenv(get_repo_root() / ".env")

# services/ -> streamingbackend/ -> guardrails/
_CONFIG_PATH = Path(__file__).resolve().parents[1] / "guardrails"

INPUT_BLOCKED_MESSAGE = (
    "I can help with Rahul's portfolio, skills, projects, and career details. "
    "What would you like to know?"
)
OUTPUT_BLOCKED_MESSAGE = (
    "I can only share details supported by Rahul's portfolio context. "
    "Ask about his skills, projects, education, or experience."
)

_config = RailsConfig.from_path(str(_CONFIG_PATH))
guardrails = LogfireRunnableRails(
    config=_config,
    passthrough=True,
    verbose=False,
    input_blocked_message=INPUT_BLOCKED_MESSAGE,
    output_blocked_message=OUTPUT_BLOCKED_MESSAGE,
)