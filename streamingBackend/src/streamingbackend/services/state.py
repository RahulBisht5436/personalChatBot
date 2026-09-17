from typing import TypedDict


class ChatbotState(TypedDict):
    user_message: str
    chat_history: list
    retrieved_context: str | None
    response: str | None
    session_id: str | None
    ui_event: dict | None
