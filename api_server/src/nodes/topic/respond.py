# LangGraph
from src.models.state import ChatState

def topic_response(state: ChatState):
    # UPDATE FINAL STATE
    state["final_answer"] = {
        "system_response": "Por favor de una pregunta mas detallada. Gracias!"
    }

    return state