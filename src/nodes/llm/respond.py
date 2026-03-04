# General
from time import perf_counter
from colorama import Fore, Style

# LangGraph
from src.models.state import ChatState

# Classes
from src.indexing.embedder import Embedder
from src.generation.searcher import Searcher
from src.generation.client import LLM_Engine

# Configuration
from config.settings import GROQ_GENERATOR_MODEL
from config.settings import GEMINI_GENERATOR_MODEL
from config.settings import LLM_SOURCE

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

async def llm_query_response(state: ChatState) -> dict:
    # Start timer
    state["start_timer_llm_generate"] = perf_counter()

    # FIXME: Prompt generation
    LLM_SOURCE  = "google"
    llm = LLM_Engine(LLM_SOURCE, GROQ_GENERATOR_MODEL, GEMINI_GENERATOR_MODEL)
    llm_response = await llm.prompt_llm(state["user_message"], state["context"])

    # Update state
    state["llm_query_response"] = f"""
        🤖 Este mensaje esta generado por Inteligencia Artifical.
        Informacion obtenida de la sección {state["document"]} del capítulo {state["chapter"]}:
        {llm_response}
        """
    logger.info(Fore.RED + f"{state['user_session_id']}: " + Style.RESET_ALL + f"{state['llm_query_response']}")
    
    state["conversation_history"].append(f"User:{state['user_message']}")
    state["conversation_history"].append(f"System:{state['llm_query_response']}")

    # Keep only the last 6 messages
    state["conversation_history"] = state["conversation_history"][-6:]

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
