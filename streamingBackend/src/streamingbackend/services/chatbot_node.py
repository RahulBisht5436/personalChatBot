from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from streamingbackend.services.state import ChatbotState
from streamingbackend.services.tools.hiring_interest_tool import (
    SEND_HIRING_INTEREST_TOOL_NAME,
    create_hiring_interest_tool,
    execute_hiring_interest_tool,
)
from streamingbackend.utility.llm_models.openai_models import llm
from streamingbackend.utility.portfolio_context import (
    BASE_ASSISTANT_INSTRUCTIONS,
    HIRING_INTEREST_INSTRUCTIONS,
)

MAX_TOOL_ITERATIONS = 3


def _build_system_content(portfolio_context: str) -> str:
    return f"{portfolio_context}\n\n{HIRING_INTEREST_INSTRUCTIONS}"


def _extract_response_content(response: object) -> str:
    if isinstance(response, str):
        return response
    content = getattr(response, "content", None)
    if isinstance(content, str):
        return content
    return str(response)


def chatbotInteractionNode(state: ChatbotState) -> dict:
    user_message = state["user_message"]
    session_id = state.get("session_id")
    chat_history = list(state.get("chat_history", []))
    portfolio_context = state.get("retrieved_context") or BASE_ASSISTANT_INSTRUCTIONS

    messages: list[BaseMessage] = [
        SystemMessage(content=_build_system_content(portfolio_context)),
        *chat_history,
        HumanMessage(content=user_message),
    ]

    llm_with_tools = llm.bind_tools([create_hiring_interest_tool(session_id)])
    ui_event: dict | None = None
    response = llm_with_tools.invoke(messages)

    for _ in range(MAX_TOOL_ITERATIONS):
        tool_calls = getattr(response, "tool_calls", None)
        if not tool_calls:
            break

        messages.append(response)
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            tool_call_id = tool_call.get("id", "")

            if tool_name == SEND_HIRING_INTEREST_TOOL_NAME:
                tool_result, event = execute_hiring_interest_tool(
                    session_id=session_id,
                    job_profile=str(tool_args.get("job_profile", "")),
                    candidate_message=str(tool_args.get("candidate_message", "")),
                    visitor_name=str(tool_args.get("visitor_name", "")),
                    visitor_email=str(tool_args.get("visitor_email", "")),
                    visitor_company=str(tool_args.get("visitor_company", "")),
                )
                if event:
                    ui_event = event
            else:
                tool_result = "Unknown tool."

            messages.append(
                ToolMessage(content=tool_result, tool_call_id=tool_call_id)
            )

        response = llm_with_tools.invoke(messages)

    response_text = _extract_response_content(response)
    assistant_message = AIMessage(content=response_text)
    updated_history = [*chat_history, HumanMessage(content=user_message), assistant_message]

    return {
        "response": response_text,
        "chat_history": updated_history,
        "ui_event": ui_event,
    }
