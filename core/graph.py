# General
import logging
from colorama import Fore, Style

# LangGraph
from langgraph.graph import StateGraph
from core.models.state import ChatState

# Nodes
from core.nodes.intent.intent import identify_intent
from core.nodes.memoria.read import read_memory
from core.nodes.memoria.update import update_memory
from core.nodes.classify.classify import classify_query
from core.nodes.clarify.clarify import ask_clarification
from core.nodes.retrieval.rag import use_rag
from core.nodes.respond.respond import respond_query

# Configuration
logger = logging.getLogger(__name__)


def _route_after_classification(state: ChatState) -> str:
    if state["user_message_ambiguos"] or state["topic_confidence"]<0.75:
        return "ask_clarification"
    if state["is_follow_up"]:
        state["llm_clarify_response"] = "use_memory"
        return "respond_query"
    else:
        state["llm_clarify_response"] = "use_rag"
        return "use_rag"

def run(user_message: object) -> str:
    # Create the graph
    graph = StateGraph(ChatState)
    user_session_id = user_message.session_id
    user_message = user_message.mensaje

    # Add nodes
    graph.add_node("intent_analysis", identify_intent)
    graph.add_node("read_memory", read_memory)
    graph.add_node("classify_query", classify_query)
    graph.add_node("ask_clarification", ask_clarification)
    graph.add_node("use_rag", use_rag)
    graph.add_node("respond_query", respond_query)
    graph.add_node("update_memory", update_memory)



    graph.set_entry_point("intent_analysis")
    graph.set_finish_point("intent_analysis")


    # # Leer memoria y clasificar la pregunta del usuario
    # graph.set_entry_point("validate_input")
    # graph.add_edge("read_memory", "classify_query")
    
    # # Decidir: Preguntar clarificacion, rag o memoria
    # graph.add_conditional_edges("classify_query", _route_after_classification)

    # # Se necesita preguntar clarificacion
    # graph.set_finish_point("ask_clarification")

    # # Se necesita usar RAG
    # graph.add_edge("use_rag", "respond_query")

    # # Se necesita usar memoria
    # graph.add_edge("respond_query", "update_memory")
    # graph.set_finish_point("update_memory")

    # Compile the graph
    app = graph.compile()

    # Invoke the graph
    final_state = app.invoke({
        "user_session_id": user_session_id,
        "user_message": user_message,
        "user_message_format": "text"
    })

    return final_state

if __name__ == "__main__":
    run()