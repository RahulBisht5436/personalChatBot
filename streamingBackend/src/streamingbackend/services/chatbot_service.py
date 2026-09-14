from langsmith import traceable

from streamingbackend.database.memory_store import load_chat_history, save_chat_history
from streamingbackend.graph import graph as compiled_graph
from streamingbackend.services.visitor_auth_service import (
    ensure_can_chat,
    register_chat_message,
)


@traceable(name="retrieve_context_node" ,run_type="tool")
def _serialize_history(chat_history: list) -> list[dict[str, str]]:
    return [
        {"role": message.type, "content": message.content}
        for message in chat_history
    ]


@traceable(name="retrieve_context_node" ,run_type="tool")
def chatbotService(user_message: str, session_id: str | None = None) -> dict:
    ensure_can_chat(session_id)
    chat_history = load_chat_history(session_id)

    result = compiled_graph.invoke(
        {
            "user_message": user_message,
            "chat_history": chat_history,
            "retrieved_context": None,
            "response": None,
        }
    )

    save_chat_history(result["chat_history"], session_id)
    access = register_chat_message(session_id)

    return {
        "response": result["response"] or "",
        "chat_history": _serialize_history(result["chat_history"]),
        "access": access,
    }


@traceable(name="retrieve_context_node" ,run_type="tool")
def getChatHistory(session_id: str | None = None) -> list[dict[str, str]]:
    chat_history = load_chat_history(session_id)
    return _serialize_history(chat_history)
