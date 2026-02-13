# LangGraph
from src.models.state import ChatState

def respond_intent(state: ChatState) -> dict:
    # Si la intencion es vacia o la confianza en la respuesta es baja devolver menu
    if state["llm_intent_response"] == "nula":
        state['llm_intent_response'] = "Menu"
    if state['intent_confidence'] < 0.5:
        state['llm_intent_response'] = "Menu"

    # UPDATE FINAL STATE
    state["final_answer"] = {
        "llm_intent_response": state["llm_intent_response"],
        "intent_confidence": state["intent_confidence"],
        "slots": state["slots"]
    }

    return state