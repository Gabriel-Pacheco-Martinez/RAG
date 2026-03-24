# LangGraph
from src.models.state import ChatState

async def intent_response(state: ChatState) -> ChatState:
    # Empty intent/"nula"
    if state.get("intent_llm") == "nula" or state.get("intent_score", 0) < 0.5:
        state["intent_llm"] = "Menu"

    # Response state
    state["final_answer"] = {
        "mensaje": state.get("user_message_str"),
        "intent_llm": state.get("intent_llm"),
        "intent_score": state.get("intent_score"),
        "required_slots": state.get("required_slots")
    }

    return state