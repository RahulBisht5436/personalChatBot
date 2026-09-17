import os

BASE_ASSISTANT_INSTRUCTIONS = """
You are Rahul AI, the friendly portfolio assistant for Rahul Bisht.

Your job is to help visitors on Rahul's portfolio website learn about him.
Answer clearly, warmly, and concisely in first person when speaking as Rahul's assistant.
Do not invent employers, grades, projects, or dates that are not in the provided context.

When the visitor asks for a resume, CV, PDF, or project link, include the exact markdown
link provided in the context using format [label](url). Make the link easy to click.

When the visitor asks how to contact Rahul, for hiring, collaboration, email, phone,
LinkedIn, or GitHub, share the public contact details listed in the context below.
These are intentionally public portfolio contact methods for recruiters and visitors.
"""

CONTACT_QUERY_KEYWORDS = (
    "contact",
    "email",
    "mail",
    "phone",
    "mobile",
    "number",
    "reach",
    "hire",
    "linkedin",
    "github",
    "connect",
    "call",
    "whatsapp",
)


def _contact_env_value(name: str) -> str:
    return os.getenv(name, "").strip()


def build_public_contact_lines() -> list[str]:
    lines: list[str] = []

    email = _contact_env_value("PORTFOLIO_CONTACT_EMAIL")
    phone = _contact_env_value("PORTFOLIO_CONTACT_PHONE")
    linkedin = _contact_env_value("PORTFOLIO_LINKEDIN_URL")
    github = _contact_env_value("PORTFOLIO_GITHUB_URL")

    if email:
        lines.append(f"- Email: {email}")
    if phone:
        lines.append(f"- Phone: {phone}")
    if linkedin:
        lines.append(f"- LinkedIn: {linkedin}")
    if github:
        lines.append(f"- GitHub: {github}")

    return lines


def format_public_contact_context() -> str:
    lines = build_public_contact_lines()
    if not lines:
        return ""
    return (
        "Public contact details (share these when the visitor asks how to reach Rahul):\n"
        + "\n".join(lines)
    )


def is_contact_query(query: str) -> bool:
    normalized = query.lower()
    return any(keyword in normalized for keyword in CONTACT_QUERY_KEYWORDS)


def build_fallback_portfolio_context() -> str:
    sections = [
        BASE_ASSISTANT_INSTRUCTIONS,
        (
            "Known profile (fallback when no documents are ingested yet):\n"
            "- Name: Rahul Bisht\n"
            "- Education: B.Tech\n"
            "- Focus areas: AI, LangGraph, FastAPI, Python, full-stack development\n"
            "- Current work: Building AI-powered apps including chatbots and streaming backends\n"
            "- Strengths: Backend APIs, LangGraph workflows, LLM integration, Next.js frontends"
        ),
    ]
    contact_context = format_public_contact_context()
    if contact_context:
        sections.append(contact_context)
    return "\n\n".join(sections)


# Backward-compatible alias used before RAG retrieval runs.
PORTFOLIO_CONTEXT = build_fallback_portfolio_context()
