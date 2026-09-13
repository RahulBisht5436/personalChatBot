from langgraph.graph import END, START, StateGraph

from streamingbackend.database.memory_store import load_chat_history, save_chat_history
from streamingbackend.services.chatbot_node import chatbotInteractionNode
from streamingbackend.services.retrieve_node import retrieveContextNode
from streamingbackend.services.state import ChatbotState
from streamingbackend.services.visitor_auth_service import (
    build_access_status,
    ensure_can_chat,
    register_chat_message,
)

graph = StateGraph(ChatbotState)
graph.add_node("retrieve_context", retrieveContextNode)
graph.add_node("chatbot_interaction", chatbotInteractionNode)
graph.add_edge(START, "retrieve_context")
graph.add_edge("retrieve_context", "chatbot_interaction")
graph.add_edge("chatbot_interaction", END)

compiled_graph = graph.compile()


def _serialize_history(chat_history: list) -> list[dict[str, str]]:
    return [
        {"role": message.type, "content": message.content}
        for message in chat_history
    ]


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


def getChatHistory(session_id: str | None = None) -> list[dict[str, str]]:
    chat_history = load_chat_history(session_id)
    return _serialize_history(chat_history)
