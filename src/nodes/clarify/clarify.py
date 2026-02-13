# LangGraph
from src.models.state import ChatState

def ask_clarification(state: ChatState):
    state["llm_clarify_response"] = "clarification_needed"

    # UPDATE FINAL STATE
    state["final_answer"] = {
        "llm_clarify_response": "Por favor de una pregunta mas clara/detallada."
    }

    return state