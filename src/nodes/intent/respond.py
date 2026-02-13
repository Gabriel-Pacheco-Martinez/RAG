# LangGraph
from src.models.state import ChatState

def respond_intent(state: ChatState) -> dict:
    # Si la intencion es vacia o la confianza en la respuesta
    # muy baja devolver el menu
    if state["llm_intent_response"] == "nula":
        state['llm_intent_response'] = "Menu"
    if state['intent_confidence'] < 0.5:
        state['llm_intent_response'] = "Menu"

    return state