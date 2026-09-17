import re
from datetime import datetime, timedelta, timezone

from streamingbackend.database.visitor_auth_store import load_auth_state, save_auth_state
from streamingbackend.utility.app_config import FREE_CHAT_LIMIT, OTP_EXPIRY_MINUTES
from streamingbackend.utility.email_service import (
    EmailDeliveryError,
    generate_otp,
    hash_otp,
    send_hiring_interest_email,
    send_lead_notification,
    send_otp_email,
)

MAX_JOB_PROFILE_LEN = 200
MAX_CANDIDATE_MESSAGE_LEN = 2000
HIRING_INTEREST_COOLDOWN_HOURS = 24

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def build_access_status(session_id: str | None = None) -> dict:
    state = load_auth_state(session_id)
    verified = bool(state.get("verified"))
    message_count = int(state.get("message_count", 0))
    requires_verification = not verified and message_count >= FREE_CHAT_LIMIT
    can_chat = verified or message_count < FREE_CHAT_LIMIT

    return {
        "verified": verified,
        "message_count": message_count,
        "free_limit": FREE_CHAT_LIMIT,
        "requires_verification": requires_verification,
        "can_chat": can_chat,
        "lead_submitted": state.get("lead") is not None,
        "hiring_interest_sent": state.get("hiring_interest_sent_at") is not None,
        "remaining_free_messages": max(FREE_CHAT_LIMIT - message_count, 0)
        if not verified
        else None,
    }


def ensure_can_chat(session_id: str | None = None) -> dict:
    access = build_access_status(session_id)
    if not access["can_chat"]:
        raise PermissionError("Verification required before continuing the chat.")
    return access


def register_chat_message(session_id: str | None = None) -> dict:
    state = load_auth_state(session_id)
    if state.get("verified"):
        return build_access_status(session_id)

    state["message_count"] = int(state.get("message_count", 0)) + 1
    save_auth_state(session_id, state)
    return build_access_status(session_id)


def submit_lead(
    session_id: str | None,
    name: str,
    email: str,
    company: str,
    designation: str,
) -> dict:
    cleaned_name = name.strip()
    cleaned_email = email.strip().lower()
    cleaned_company = company.strip()
    cleaned_designation = designation.strip()

    if not cleaned_name or not cleaned_company or not cleaned_designation:
        raise ValueError("Name, company, and designation are required.")
    if not EMAIL_PATTERN.fullmatch(cleaned_email):
        raise ValueError("Enter a valid email address.")

    otp = generate_otp()
    state = load_auth_state(session_id)
    state["lead"] = {
        "name": cleaned_name,
        "email": cleaned_email,
        "company": cleaned_company,
        "designation": cleaned_designation,
    }
    state["otp_hash"] = hash_otp(otp)
    state["otp_expires_at"] = (
        _utc_now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    ).isoformat()
    state["lead_submitted_at"] = _utc_now().isoformat()
    save_auth_state(session_id, state)

    try:
        send_otp_email(cleaned_email, cleaned_name, otp)
    except EmailDeliveryError as error:
        raise ValueError(str(error)) from error

    return {
        "message": "OTP sent to your email address.",
        "access": build_access_status(session_id),
    }


def resend_otp(session_id: str | None) -> dict:
    state = load_auth_state(session_id)
    lead = state.get("lead")

    if not lead:
        raise ValueError("Submit your details first to receive an OTP.")

    otp = generate_otp()
    state["otp_hash"] = hash_otp(otp)
    state["otp_expires_at"] = (
        _utc_now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    ).isoformat()
    save_auth_state(session_id, state)

    try:
        send_otp_email(lead["email"], lead["name"], otp)
    except EmailDeliveryError as error:
        raise ValueError(str(error)) from error

    return {
        "message": "A new verification code has been sent to your email.",
        "access": build_access_status(session_id),
    }


def verify_otp(session_id: str | None, otp: str) -> dict:
    cleaned_otp = otp.strip()
    if not cleaned_otp:
        raise ValueError("OTP is required.")

    state = load_auth_state(session_id)
    lead = state.get("lead")
    otp_hash = state.get("otp_hash")
    otp_expires_at = _parse_datetime(state.get("otp_expires_at"))

    if not lead or not otp_hash:
        raise ValueError("Submit your details first to receive an OTP.")
    if otp_expires_at and _utc_now() > otp_expires_at:
        raise ValueError("OTP has expired. Request a new one.")

    if hash_otp(cleaned_otp) != otp_hash:
        raise ValueError("Invalid OTP. Please try again.")

    state["verified"] = True
    state["verified_at"] = _utc_now().isoformat()
    state["otp_hash"] = None
    state["otp_expires_at"] = None
    save_auth_state(session_id, state)

    lead_with_session = {**lead, "session_id": session_id}
    try:
        send_lead_notification(lead_with_session)
    except EmailDeliveryError as error:
        raise ValueError(str(error)) from error

    return {
        "message": "Email verified. You can continue chatting.",
        "access": build_access_status(session_id),
    }


def submit_hiring_interest(
    session_id: str | None,
    job_profile: str,
    candidate_message: str,
    visitor_name: str = "",
    visitor_email: str = "",
    visitor_company: str = "",
) -> tuple[str, dict | None]:
    cleaned_job_profile = job_profile.strip()
    cleaned_message = candidate_message.strip() or "(No additional message provided)"

    if not cleaned_job_profile:
        return (
            "Job profile is required. Ask the visitor which role or position they are hiring for.",
            None,
        )
    if len(cleaned_job_profile) > MAX_JOB_PROFILE_LEN:
        return (
            f"Job profile is too long (max {MAX_JOB_PROFILE_LEN} characters). Ask for a shorter summary.",
            None,
        )
    if len(cleaned_message) > MAX_CANDIDATE_MESSAGE_LEN:
        return (
            f"Message is too long (max {MAX_CANDIDATE_MESSAGE_LEN} characters). Ask for a shorter note.",
            None,
        )

    state = load_auth_state(session_id)
    lead = state.get("lead")

    resolved_name = (lead or {}).get("name") or visitor_name.strip()
    resolved_email = (lead or {}).get("email") or visitor_email.strip().lower()
    resolved_company = (lead or {}).get("company") or visitor_company.strip()

    if not resolved_name or not resolved_email or not resolved_company:
        return (
            "Visitor contact details are missing. Ask for their name, email, and company in the chat. "
            "Do not ask for an OTP. Once collected, call send_hiring_interest with visitor_name, "
            "visitor_email, visitor_company, job_profile, and candidate_message.",
            None,
        )
    if not EMAIL_PATTERN.fullmatch(resolved_email):
        return (
            "The email address is invalid. Ask the visitor for a valid email address.",
            None,
        )

    sent_at = _parse_datetime(state.get("hiring_interest_sent_at"))
    if sent_at and _utc_now() - sent_at < timedelta(hours=HIRING_INTEREST_COOLDOWN_HOURS):
        return (
            "A hiring interest email was already sent recently for this session. "
            "Tell the visitor Rahul has been notified and will follow up soon.",
            None,
        )

    try:
        send_hiring_interest_email(
            visitor_name=resolved_name,
            visitor_email=resolved_email,
            visitor_company=resolved_company,
            job_profile=cleaned_job_profile,
            candidate_message=cleaned_message,
            session_id=session_id or "unknown",
        )
    except EmailDeliveryError as error:
        return (f"Could not send the email: {error}", None)

    state["hiring_interest_sent_at"] = _utc_now().isoformat()
    save_auth_state(session_id, state)

    ui_event = {
        "type": "hiring_interest_sent",
        "launcher_mood": "happy",
    }
    return (
        "Hiring interest email sent successfully to Rahul. "
        "Confirm to the visitor that Rahul has been notified and will review their message "
        "as soon as possible.",
        ui_event,
    )
