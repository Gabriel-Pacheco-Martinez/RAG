# General
from colorama import Fore, Style
from time import perf_counter

# LangGraph
from src.models.state import ChatState

# Helpers
from src.utils.redis import deserialize_session_data,serialize_session_data

# Configuration
from config.settings import settings
from config.settings import REDIS_CLIENT

# Logging 
import logging
logger = logging.getLogger('uvicorn.error')

async def update_memory(state: ChatState) -> ChatState:
    # Timer
    state["start_timer_memory_update"] = perf_counter()

    # Read Redis data
    session_id = str(state["user_session_id"])
    session_ttl: int = settings.REDIS_TTL_SECONDS
    session_data: dict[str, str] = await REDIS_CLIENT.hgetall(session_id)
    session_data_obj = deserialize_session_data(session_data)

    # Update states
    session_data_obj["topic_previous"] = state.get("topic_llm")
    session_data_obj["context"] = state.get("context")
    session_data_obj["conversation_history"] = state.get("conversation_history")
    session_data_obj["document_previous"] = state.get("document")
    session_data_obj["chapter_previous"] = state.get("chapter")

    # Update redis data
    session_data = serialize_session_data(session_data_obj)
    await REDIS_CLIENT.hset(session_id, mapping=session_data)
    await REDIS_CLIENT.expire(session_id, session_ttl)

    # Timer
    logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + "[✅] 💿 MEMORY UPDATED: " + Style.RESET_ALL + "it took " + Fore.YELLOW + f"{perf_counter() - state['start_timer_memory_update']:.4f}s ⏱. " + Style.RESET_ALL + f"Session {session_id}: updated with TTL of {session_ttl} seconds.")
    return state

