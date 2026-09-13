from streamingbackend.rag.retrieve_service import retrieve_career_context
from streamingbackend.services.state import ChatbotState


def retrieveContextNode(state: ChatbotState) -> dict:
    user_message = state["user_message"]
    retrieved_context = retrieve_career_context(user_message)
    return {"retrieved_context": retrieved_context}
