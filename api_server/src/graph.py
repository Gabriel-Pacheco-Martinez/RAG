"""
Author: Gabriel Pacheco
Date: February 2026
"""
# General
import logging
from colorama import Fore, Style

# Helpers
from src.models.query import QueryRequest
from src.utils.error_responses import build_error_response
from src.utils.error_responses import get_error_status_code
from src.utils.llm import calculate_cost

# LangGraph
from langgraph.graph import StateGraph
from src.models.state import ChatState

# Nodes
from src.nodes.intent.detect import intent_detect
from src.nodes.intent.respond import intent_response
from src.nodes.memory.read import read_memory
from src.nodes.memory.update import update_memory
from src.nodes.topic.detect import topic_detect
from src.nodes.topic.respond import topic_response
from src.nodes.generate.client import llm_generate
from src.nodes.generate.respond import llm_response

# Decorators
from src.utils.decorators import safe_node
from src.utils.decorators import route_or_error

# Configuration
logger = logging.getLogger('uvicorn.error')

# =========
# ERRORS
def error_handler(state: ChatState) -> ChatState:
    error_message = build_error_response(state.get("error_data"))
    error_status_code = get_error_status_code(state.get("error_data"))

    state["final_answer"] = {
        "status": error_status_code,
        "message": error_message,
        "data": state.get("error_data")
    }
    return state

# =========
# ROUTE TOPIC
def topic_route(state: ChatState) -> str:
    # Error detected
    if state.get("error"):
        return "error_handler"

    # Topic ambiguous
    if state.get("suggested_clarification"):
        logger.info("Reaching back to the user for clarification.")
        return "topic_response"

    if state.get("topic_ambiguous") or state.get("topic_score", 0) < 0.75:
        logger.info("Topic is ambiguous. We will reach back to the user.")
        return "topic_response"
    
    # RAG or MEMORY
    return "llm_generate"

async def run(request: QueryRequest) -> tuple[dict, dict]:
    # User input message information
    user_session_id = request.session_id
    user_message = request.mensaje
    user_message_format = ""
    if isinstance(user_message, str):
        user_message_format = "text"
    elif isinstance(user_message, bytes):
        user_message_format = "audio"

    initial_state: ChatState = {
        "user_message": user_message,
        "user_session_id": user_session_id,
        "user_message_format": user_message_format,
        "token_count_input": 0,
        "token_count_output": 0
    }

    # Invoke graph
    final_state = await app.ainvoke(initial_state)

    # Cost and tokens calculation
    input_tokens = final_state['token_count_input']
    output_tokens = final_state['token_count_output']
    cost = calculate_cost(input_tokens, output_tokens)
    logger.info(Fore.RED + f"{final_state['user_session_id']}: " + Fore.YELLOW + f"💰 Estimated cost of the query: ${cost:.6f} for {input_tokens} input tokens and {output_tokens} output tokens" + Style.RESET_ALL)

    usage_data = {
        "cost": cost,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens
    }

    # Return final answer and usage data
    return final_state["final_answer"], usage_data


# =========
# Create the graph
graph = StateGraph(ChatState)

# =========
# Nodes:
graph.add_node("intent_detect", safe_node("intent_detect")(intent_detect))
graph.add_node("intent_response", safe_node("intent_response")(intent_response))
graph.add_node("read_memory", safe_node("read_memory")(read_memory))
graph.add_node("topic_detect", safe_node("topic_detect")(topic_detect))
graph.add_node("topic_response", safe_node("topic_response")(topic_response))
graph.add_node("llm_generate", safe_node("llm_generate")(llm_generate))
graph.add_node("llm_response", safe_node("llm_response")(llm_response))
graph.add_node("update_memory", safe_node("update_memory")(update_memory))
graph.add_node("error_handler", error_handler)

# =========
# FIXME:Routing-Edges:
#   1. Detectar el intent del usuario
graph.set_entry_point("intent_detect")

#   2. Detectar el topic de la pregunta del usuario
graph.add_conditional_edges("intent_detect", route_or_error("read_memory"))
graph.add_conditional_edges("read_memory", route_or_error("topic_detect"))
graph.add_conditional_edges("topic_detect", topic_route)
graph.add_edge("topic_response", "__end__")
graph.add_edge("error_handler", "__end__")

#   3. Contestar la pregunta del usuario
graph.add_conditional_edges("llm_generate", route_or_error("llm_response"))
graph.add_conditional_edges("llm_response", route_or_error("update_memory"))
graph.add_conditional_edges("update_memory", route_or_error("__end__"))

# =========
# Execution:
app = graph.compile()