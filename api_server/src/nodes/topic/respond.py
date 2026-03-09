# LangGraph
from src.models.state import ChatState

def topic_response(state: ChatState):
    # There is suggested clarification
    if state.get("suggested_clarification"):
        state["final_answer"] = {
            "system_response": state.get("suggested_clarification")
        }
        return state

    # No suggested clarification
    state["final_answer"] = {
        "system_response": "Por favor de una pregunta mas detallada. Gracias!"
    }

    return state