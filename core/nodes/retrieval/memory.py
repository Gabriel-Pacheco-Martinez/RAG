# LangGraph
from core.models.state import ChatState

def use_memory(state: ChatState):
    state["llm_clarify_response"] = "We will use memory"
    return state
