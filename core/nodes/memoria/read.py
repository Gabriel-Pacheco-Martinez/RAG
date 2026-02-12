# General
from colorama import Fore, Style
import json

# LangGraph
from core.models.state import ChatState

# Helpers
from core.utils.redis import deserialize_session_data

# Configuration
from config.settings import REDIS_CLIENT
from config.settings import REDIS_TTL_SECONDS

# Logging 
import logging
logger = logging.getLogger(__name__)

def read_memory(state: ChatState) -> dict:
    session_id = str(state["user_session_id"])
    session_ttl = REDIS_TTL_SECONDS
    session_data = REDIS_CLIENT.hgetall(session_id)
    
    # Session just started
    if not session_data:
        # Redis
        REDIS_CLIENT.hset(session_id, mapping={
            "topic_previous": json.dumps(""),
            "conversation_history": json.dumps([]),
            "context": json.dumps("")
        })

        # State
        state["topic_previous"] = ""
        state["conversation_history"] = []
        state["context"] = ""

        # Set TTL
        REDIS_CLIENT.expire(session_id, session_ttl)
        logger.info(f"Session {session_id}: created with TTL of {session_ttl} seconds")

    else:
        # State
        session_data_obj = deserialize_session_data(session_data)
        state["topic_previous"] = session_data_obj.get("topic_previous", "")
        state["conversation_history"] = session_data_obj.get("conversation_history", "")
        state["context"] = session_data_obj.get("context", "")
        logger.info(f"Session {session_id}: read and loaded")

    return state

