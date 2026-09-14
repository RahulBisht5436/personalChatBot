from streamingbackend.rag.retrieve_service import retrieve_career_context
from streamingbackend.services.state import ChatbotState
from langsmith import traceable , get_current_run_tree



@traceable(name="retrieve_context_node" ,run_type="tool")
def retrieveContextNode(state: ChatbotState) -> dict:
    run_tree = get_current_run_tree()
    if run_tree:
        print(run_tree.name)
        run_tree.metadata.update({"user_message": state["user_message"]})
    user_message = state["user_message"]
    retrieved_context = retrieve_career_context(user_message)
    return {"retrieved_context": retrieved_context}
