"""
Author: Gabriel Pacheco
Date: February 2026
"""
# General
import logging
from colorama import Fore, Style

# Helpers
from src.utils.error_responses import build_error_response

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

# Decorators
from src.utils.decorators import safe_node
from src.utils.decorators import route_or_error

# Configuration
logger = logging.getLogger('uvicorn.error')

def intent_route(state: ChatState) -> str:
    # Si hay un error
    if state.get("error"):
        return "error_handler"

    # Elegir el siguiente node
    if state["llm_intent_response"] == "preguntas":
        logger.info("Intent is 'preguntas'. We will now read memory.")
        return "read_memory"
    else:
        logger.info("Intent is not 'preguntas'.")
        return "intent_guardrail_response"

def topic_route(state: ChatState) -> str:
    # Si hay un error
    if state.get("error"):
        return "error_handler"

    # Elegir el siguiente node
    if state["user_message_ambiguous"] or state["topic_confidence"]<0.75:
        logger.info("Query is ambiguous. We will reach back to user.")
        return "topic_guardrail_response"
    if state["info_source"] == "memory":
        logger.info("We will use memory to answer the query.")
        return "llm_response"
    elif state["info_source"] == "rag":
        logger.info("We will use RAG to answer the query.")
        return "llm_rag"

def error_handler(state: ChatState) -> ChatState:
    error = state.get("error") # If it doent exist, it returns None (.get())
    logger.error(f"[❌] Workflow failed at {error}")

    response_message = build_error_response(error)

    state["final_answer"] = {
        "response": response_message,
        "error": error
    }
    return state

def run(user_message: object) -> str:
    # Create the graph
    graph = StateGraph(ChatState)

    # User message
    user_session_id = user_message.session_id
    user_message = user_message.mensaje
    if isinstance(user_message, str):
        user_message_format = "text"
    elif isinstance(user_message, bytes):
        user_message_format = "audio"

    # =========
    # Nodes:
    graph.add_node("intent_detect", safe_node("intent_detect")(intent_detect))
    graph.add_node("intent_guardrail_response", safe_node("intent_guardrail_response")(intent_guardrail_response))
    graph.add_node("read_memory", safe_node("read_memory")(read_memory))
    graph.add_node("topic_detect", safe_node("topic_detect")(topic_detect))
    graph.add_node("topic_guardrail_response", safe_node("topic_guardrail_response")(topic_guardrail_response))
    graph.add_node("llm_rag", safe_node("llm_rag")(llm_rag_retrieval))
    graph.add_node("llm_response", safe_node("llm_query_response")(llm_query_response))
    graph.add_node("update_memory", safe_node("update_memory")(update_memory))
    graph.add_node("error_handler", error_handler)

    # =========
    # Routing-Edges:
    #   1. Detectar el intent del usuario
    graph.set_entry_point("intent_detect")
    graph.add_conditional_edges("intent_detect", intent_route)

    #   2. Detectar el topic de la pregunta del usuario
    graph.add_conditional_edges("read_memory", route_or_error("topic_detect"))
    graph.add_conditional_edges("topic_detect", topic_route)

    #   3. Contestar la pregunta del usuario
    graph.add_conditional_edges("llm_rag", route_or_error("llm_response"))
    graph.add_conditional_edges("llm_response", route_or_error("update_memory"))
    graph.add_conditional_edges("update_memory", route_or_error("__end__"))

    # =========
    # Execution:
    app = graph.compile()
    final_state = app.invoke({
        "user_session_id": user_session_id,
        "user_message": user_message,
        "user_message_format": user_message_format
    })

    return final_state["final_answer"]

if __name__ == "__main__":
    run()