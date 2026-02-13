# General
import json

# LangGraph
from src.models.state import ChatState

# Helpers
from src.utils.redis import deserialize_session_data,serialize_session_data

# Configuration
from config.settings import REDIS_CLIENT
from config.settings import REDIS_TTL_SECONDS

# Logging 
import logging
logger = logging.getLogger(__name__)

def update_memory(state: ChatState) -> None:
    # Read Redis data
    session_id = str(state["user_session_id"])
    session_ttl = REDIS_TTL_SECONDS
    session_data = REDIS_CLIENT.hgetall(session_id)
    session_data_obj = deserialize_session_data(session_data)

    # Update states
    session_data_obj["topic_previous"] = state["topic"]
    session_data_obj["context"] = state["context"]
    session_data_obj["conversation_history"] = state["conversation_history"]

    # Update redis data
    session_data = serialize_session_data(session_data_obj)
    REDIS_CLIENT.hset(session_id, mapping=session_data)
    REDIS_CLIENT.expire(session_id, session_ttl)
