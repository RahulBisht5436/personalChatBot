"""LangGraph definition exported for LangGraph CLI / Studio."""

from langgraph.graph import END, START, StateGraph

from streamingbackend.services.chatbot_node import chatbotInteractionNode
from streamingbackend.services.retrieve_node import retrieveContextNode
from streamingbackend.services.state import ChatbotState


def build_graph() -> StateGraph:
    workflow = StateGraph(ChatbotState)
    workflow.add_node("retrieve_context", retrieveContextNode)
    workflow.add_node("chatbot_interaction", chatbotInteractionNode)
    workflow.add_edge(START, "retrieve_context")
    workflow.add_edge("retrieve_context", "chatbot_interaction")
    workflow.add_edge("chatbot_interaction", END)
    return workflow


# LangGraph CLI expects a compiled graph at this symbol.
graph = build_graph().compile()
