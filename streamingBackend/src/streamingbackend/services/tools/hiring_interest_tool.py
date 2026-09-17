from langchain_core.tools import StructuredTool

from streamingbackend.services.visitor_auth_service import submit_hiring_interest

SEND_HIRING_INTEREST_TOOL_NAME = "send_hiring_interest"


def create_hiring_interest_tool(session_id: str | None) -> StructuredTool:
    def _send_hiring_interest(
        job_profile: str,
        candidate_message: str = "",
        visitor_name: str = "",
        visitor_email: str = "",
        visitor_company: str = "",
    ) -> str:
        result, _ui_event = submit_hiring_interest(
            session_id=session_id,
            job_profile=job_profile,
            candidate_message=candidate_message,
            visitor_name=visitor_name,
            visitor_email=visitor_email,
            visitor_company=visitor_company,
        )
        return result

    return StructuredTool.from_function(
        func=_send_hiring_interest,
        name=SEND_HIRING_INTEREST_TOOL_NAME,
        description=(
            "Send a hiring interest email to Rahul on behalf of the visitor. "
            "Use when the visitor wants to hire Rahul or discuss a job opportunity. "
            "Required: job_profile. Also pass visitor_name, visitor_email, and visitor_company "
            "if not already known from a prior verification flow. "
            "candidate_message is optional. Never ask for an OTP."
        ),
    )


def execute_hiring_interest_tool(
    session_id: str | None,
    job_profile: str,
    candidate_message: str,
    visitor_name: str = "",
    visitor_email: str = "",
    visitor_company: str = "",
) -> tuple[str, dict | None]:
    return submit_hiring_interest(
        session_id=session_id,
        job_profile=job_profile,
        candidate_message=candidate_message,
        visitor_name=visitor_name,
        visitor_email=visitor_email,
        visitor_company=visitor_company,
    )
