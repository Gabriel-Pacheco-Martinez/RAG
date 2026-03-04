# General
import json
from colorama import Fore, Style
from time import perf_counter

# LangGraph
from src.models.state import ChatState

# Helpers
from src.utils.redis import deserialize_session_data

# Configuration
from config.settings import REDIS_CLIENT
from config.settings import REDIS_TTL_SECONDS

# Logging 
import logging
logger = logging.getLogger('uvicorn.error')

def read_memory(state: ChatState) -> dict:
    # Start timer
    state["start_timer_memory_read"] = perf_counter()

    session_id = str(state["user_session_id"])
    session_ttl = REDIS_TTL_SECONDS
    session_data = REDIS_CLIENT.hgetall(session_id)
    
    # Session just started
    if not session_data:
        # Redis
        REDIS_CLIENT.hset(session_id, mapping={
            "topic_previous": json.dumps(""),
            "conversation_history": json.dumps([]),
            "context": json.dumps(""),
            "document_previous": json.dumps(""),
            "chapter_previous": json.dumps("")
        })

        # State
        state["topic_previous"] = ""
        state["conversation_history"] = []
        state["context"] = ""
        state["document_previous"] = ""
        state["chapter_previous"] = ""

        # Set TTL
        REDIS_CLIENT.expire(session_id, session_ttl)

        # Timer
        logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + "[✅] 💿 MEMORY READ: " + Style.RESET_ALL + "it took " + Fore.YELLOW + f"{perf_counter() - state['start_timer_memory_read']:.4f}s ⏱. " + Style.RESET_ALL + f"Session {session_id}: created with TTL of {session_ttl} seconds.")

    else:
        # State
        session_data_obj = deserialize_session_data(session_data)
        state["topic_previous"] = session_data_obj.get("topic_previous", "")
        state["conversation_history"] = session_data_obj.get("conversation_history", "")
        state["context"] = session_data_obj.get("context", "")
        state["document"] = session_data_obj.get("document_previous", "")
        state["chapter"] = session_data_obj.get("chapter_previous", "")

        # Timer
        logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + "[✅] 💿 MEMORY READ: " + Style.RESET_ALL + "it took " + Fore.YELLOW + f"{perf_counter() - state['start_timer_memory_read']:.4f}s ⏱. " + Style.RESET_ALL + f"Session {session_id}: read and loaded.")

    return state

