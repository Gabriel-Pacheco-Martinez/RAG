# LangGraph
from src.models.state import ChatState

def ask_clarification(state: ChatState):
    state["llm_clarify_response"] = "clarification_needed"
    return state