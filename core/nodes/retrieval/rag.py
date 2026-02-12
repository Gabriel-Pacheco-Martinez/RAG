# LangGraph
from core.models.state import ChatState

def use_rag(state: ChatState):
    state["llm_clarify_response"] = "We will use rag"
    return state