"""
Author: Gabriel Pacheco
Date: February 2026
"""
# General
import logging
from colorama import Fore, Style

# LangGraph
from langgraph.graph import StateGraph
from src.models.state import ChatState

# Nodes
from src.nodes.intent.detect import intent_detect
from src.nodes.intent.respond import intent_guardrail_response
from src.nodes.memory.read import read_memory
from src.nodes.memory.update import update_memory
from src.nodes.topic.detect import topic_detect
from src.nodes.topic.respond import topic_guardrail_response
from src.nodes.llm.rag import llm_rag_retrieval
from src.nodes.llm.respond import llm_query_response

# Configuration
logger = logging.getLogger(__name__)

def intent_route(state: ChatState) -> str:
    # Si el usuario quiere que se le responda una pregunta
    if state["llm_intent_response"] == "preguntas":
        return "read_memory"
    # Si el usuario necesitaba las otras preguntas
    else:
        return "intent_guardrail_response"

def topic_route(state: ChatState) -> str:
    # Si la pregunta es demasiado ambigua
    if state["user_message_ambiguous"] or state["topic_confidence"]<0.75:
        return "topic_guardrail_response"
    # Si la informacion viene de la memoria
    if state["info_source"] == "memory":
        return "llm_response"
    # Si la informacion hay que leerla con rag
    elif state["info_source"] == "rag":
        return "llm_rag"

def run(user_message: object) -> str:
    # Create the graph
    graph = StateGraph(ChatState)
    user_session_id = user_message.session_id
    user_message = user_message.mensaje

    # =========
    # Nodes:
    graph.add_node("intent_detect", intent_detect)
    graph.add_node("intent_guardrail_response", intent_guardrail_response)
    graph.add_node("read_memory", read_memory)
    graph.add_node("topic_detect", topic_detect)
    graph.add_node("topic_guardrail_response", topic_guardrail_response)
    graph.add_node("llm_rag", llm_rag_retrieval)
    graph.add_node("llm_response", llm_query_response)
    graph.add_node("update_memory", update_memory)

    # =========
    # Routing-Edges:
    #   1. Detectar el intent del usuario
    graph.set_entry_point("intent_detect")
    graph.add_conditional_edges("intent_detect", intent_route)

    #   2. Detectar el topic de la pregunta del usuario
    graph.add_edge("read_memory", "topic_detect")
    graph.add_conditional_edges("topic_detect", topic_route)

    #   3. Contestar la pregunta del usuario
    graph.add_edge("llm_rag", "llm_response")
    graph.add_edge("llm_response", "update_memory")
    graph.set_finish_point("update_memory")

    # =========
    # Execution:
    app = graph.compile()
    final_state = app.invoke({
        "user_session_id": user_session_id,
        "user_message": user_message,
        "user_message_format": "text"
    })

    return final_state["final_answer"]

if __name__ == "__main__":
    run()