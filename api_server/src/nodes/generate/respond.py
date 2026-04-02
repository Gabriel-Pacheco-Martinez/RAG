# General
from time import perf_counter
from colorama import Fore, Style

# LangGraph
from src.models.state import ChatState

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

async def llm_response(state: ChatState) -> ChatState:
    # Check if there is an LLM response in the state
    if state.get("generate_llm") is None:
        raise ValueError("LLM response is None")

    # UPDATE FINAL STATE
    state["final_answer"] = {
        "status": 200,
        "message": state.get("generate_llm"),
        "data": {
            "topic": state.get("topic_llm"),
            "rewritten_query": state.get("user_message_str")
            # "info_source": state.get("info_source"),
            # "context": state.get("context"),
            # "conversation_history": state.get("conversation_history")
        }
    }

    return state
