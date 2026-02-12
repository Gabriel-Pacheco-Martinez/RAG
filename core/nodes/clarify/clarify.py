# LangGraph
from core.models.state import ChatState

def ask_clarification(state: ChatState):
    state["llm_clarify_response"] = "Por favor de una pregunta mas especifica."
    return state