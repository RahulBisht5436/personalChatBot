from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
import logfire

from streamingbackend.services.guardrails_service import guardrails
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

chain = prompt | (guardrails | llm)


def _format_chat_history(chat_history: list) -> str:
    lines: list[str] = []
    for message in chat_history:
        if isinstance(message, BaseMessage):
            role = "Visitor" if message.type == "human" else "Rahul AI"
            lines.append(f"{role}: {message.content}")
        else:
            lines.append(str(message))
    return "\n".join(lines) if lines else "No previous messages."


def _extract_response_content(response: object) -> str:
    if isinstance(response, str):
        return response
    content = getattr(response, "content", None)
    if isinstance(content, str):
        return content
    return str(response)


def chatbotInteractionNode(state: ChatbotState) -> dict:
    user_message = state["user_message"]
    chat_history = list(state.get("chat_history", []))
    chat_history.append(HumanMessage(content=user_message))

    with logfire.span(
        "chatbot_interaction",
        user_message=user_message,
        has_retrieved_context=bool(state.get("retrieved_context")),
    ):
        response = chain.invoke(
            {
                "user_message": user_message,
                "chat_history": _format_chat_history(chat_history[:-1]),
                "portfolio_context": state.get("retrieved_context")
                or BASE_ASSISTANT_INSTRUCTIONS,
            }
        )
        response_text = _extract_response_content(response)
        logfire.info(
            "chatbot response generated",
            response_length=len(response_text),
            response_preview=response_text[:240] if response_text else "",
        )

    assistant_message = AIMessage(content=response_text)
    chat_history.append(assistant_message)
    return {"response": response_text, "chat_history": chat_history}
