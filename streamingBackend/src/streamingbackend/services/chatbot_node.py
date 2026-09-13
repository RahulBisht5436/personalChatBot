from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import PromptTemplate

from streamingbackend.services.state import ChatbotState
from streamingbackend.utility.llm_models.openai_models import llm
from streamingbackend.utility.portfolio_context import BASE_ASSISTANT_INSTRUCTIONS

prompt = PromptTemplate(
    template="""
{portfolio_context}

Conversation so far:
{chat_history}

Visitor question: {user_message}

Reply as Rahul AI:
""",
    input_variables=["user_message", "chat_history", "portfolio_context"],
)

chain = prompt | llm


def _format_chat_history(chat_history: list) -> str:
    lines: list[str] = []
    for message in chat_history:
        if isinstance(message, BaseMessage):
            role = "Visitor" if message.type == "human" else "Rahul AI"
            lines.append(f"{role}: {message.content}")
        else:
            lines.append(str(message))
    return "\n".join(lines) if lines else "No previous messages."


def chatbotInteractionNode(state: ChatbotState) -> dict:
    user_message = state["user_message"]
    chat_history = list(state.get("chat_history", []))
    chat_history.append(HumanMessage(content=user_message))

    response = chain.invoke(
        {
            "user_message": user_message,
            "chat_history": _format_chat_history(chat_history[:-1]),
            "portfolio_context": state.get("retrieved_context")
            or BASE_ASSISTANT_INSTRUCTIONS,
        }
    )
    assistant_message = AIMessage(content=response.content)
    chat_history.append(assistant_message)
    return {"response": response.content, "chat_history": chat_history}
