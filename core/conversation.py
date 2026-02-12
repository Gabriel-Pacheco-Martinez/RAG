# General
import logging
from colorama import Fore, Style

# LangGraph
from langgraph.graph import StateGraph
from core.models.state import ChatState

# Nodes
from core.nodes.memoria.read import read_memory
from core.nodes.classify.classify import classify_query
from core.nodes.clarify.clarify import ask_clarification
from core.nodes.retrieval.memory import use_memory
from core.nodes.retrieval.rag import use_rag

# Configuration
logger = logging.getLogger(__name__)


def _route_after_classification(state: ChatState) -> str:
    if state["user_message_ambiguos"] or state["topic_confidence"]<0.75:
        return "ask_clarification"
    if state["is_follow_up"]:
        return "use_memory"
    else:
        return "use_rag"

def run(user_message: object) -> str:
    # Create the graph
    graph = StateGraph(ChatState)
    user_session_id = user_message.session_id
    user_message_text = user_message.mensaje

    # Add nodes
    graph.add_node("read_memory", read_memory)
    graph.add_node("classify_query", classify_query)
    graph.add_node("ask_clarification", ask_clarification)
    graph.add_node("use_rag", use_rag)
    graph.add_node("use_memory", use_memory)

    # Leer memoria y clasificar la pregunta del usuario
    graph.set_entry_point("read_memory")
    graph.add_edge("read_memory", "classify_query")
    
    # Decidir: Preguntar clarificacion, rag o memoria
    graph.add_conditional_edges("classify_query", _route_after_classification)

    # Se necesita preguntar clarificacion
    graph.set_finish_point("ask_clarification")

    # Se necesita usar RAG
    graph.set_finish_point("use_memory")
    graph.set_finish_point("use_rag")

    # Compile the graph
    app = graph.compile()

    # Invoke the graph
    final_state = app.invoke({
        "user_session_id": user_session_id,
        "user_message": user_message_text,
    })

    return final_state

if __name__ == "__main__":
    run()