# General
import logging
from colorama import Fore, Style

# LangGraph
from langgraph.graph import StateGraph
from src.models.state import ChatState

# Nodes
from src.nodes.intent.intent import identify_intent
from src.nodes.intent.respond import respond_intent
from src.nodes.memoria.read import read_memory
from src.nodes.memoria.update import update_memory
from src.nodes.classify.classify import classify_query
from src.nodes.clarify.clarify import ask_clarification
from src.nodes.retrieval.rag import use_rag
from src.nodes.generate.respond import respond_query

# Configuration
logger = logging.getLogger(__name__)


def _route_after_classification(state: ChatState) -> str:
    if state["user_message_ambiguous"] or state["topic_confidence"]<0.75:
        return "ask_clarification"
    if state["info_source"] == "memory":
        return "respond_query"
    elif state["info_source"] == "rag":
        return "use_rag"

def _route_after_intention(state: ChatState) -> str:
    if state["llm_intent_response"] == "preguntas":
        return "read_memory"
    else:
        return "respond_intent"

def run(user_message: object) -> str:
    # Create the graph
    graph = StateGraph(ChatState)
    user_session_id = user_message.session_id
    user_message = user_message.mensaje

    # Add nodes
    graph.add_node("intent_analysis", identify_intent)
    graph.add_node("respond_intent", respond_intent)
    graph.add_node("read_memory", read_memory)
    graph.add_node("classify_query", classify_query)
    graph.add_node("ask_clarification", ask_clarification)
    graph.add_node("use_rag", use_rag)
    graph.add_node("respond_query", respond_query)
    graph.add_node("update_memory", update_memory)

    # Identificar que quiere el usuario
    graph.set_entry_point("intent_analysis")
    graph.add_conditional_edges("intent_analysis", _route_after_intention)

    # Clasificar la pregunta del usuario
    graph.add_edge("read_memory", "classify_query")
    graph.add_conditional_edges("classify_query", _route_after_classification)

    # Contestar la pregunta con contexto
    graph.add_edge("use_rag", "respond_query")
    graph.add_edge("respond_query", "update_memory")
    graph.set_finish_point("update_memory")

    # Compile the graph
    app = graph.compile()

    # Invoke the graph
    final_state = app.invoke({
        "user_session_id": user_session_id,
        "user_message": user_message,
        "user_message_format": "text"
    })

    return final_state["final_answer"]

if __name__ == "__main__":
    run()