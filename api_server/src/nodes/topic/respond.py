# LangGraph
from src.models.state import ChatState

async def topic_response(state: ChatState):
    # There is suggested clarification
    if state.get("suggested_clarification"):
        state["final_answer"] = {
            "status": 200,
            "mensaje": state.get("suggested_clarification"),
            "data": {}
        }
        return state

    # No suggested clarification
    state["final_answer"] = {
        "status": 200,
        "mensaje": "Por favor de una pregunta mas detallada.",
        "data": {}
    }

    return state