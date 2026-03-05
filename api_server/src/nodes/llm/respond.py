# General
from time import perf_counter
from colorama import Fore, Style

# LangGraph
from src.models.state import ChatState

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

async def llm_response(state: ChatState) -> ChatState:
    # UPDATE FINAL STATE
    state["final_answer"] = {
        "topic": state["topic"],
        "rewritten_query": state["rewritten_query"],
        "info_source": state["info_source"],
        "response": state["llm_query_response"],
        "context": state["context"],
        "conversation_history": state["conversation_history"]
    }

    # Timer
    logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + "[✅] 👾 QUERY ANSWERED: " + Style.RESET_ALL + "it took " + Fore.YELLOW + f"{perf_counter() - state['start_timer_llm_generate']:.4f}s ⏱. ")

    return state
