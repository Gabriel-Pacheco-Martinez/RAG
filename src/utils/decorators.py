# General
import logging

# Classes
from src.models.state import ChatState

# Configuration
logger = logging.getLogger(__name__)

def safe_node(node_name: str):
    def decorator(func):
        def wrapper(state: ChatState) -> ChatState:
            try:
                return func(state)

            except Exception as e:
                logger.exception(f"Error in node {node_name}")

                state["error"] = {
                    "node": node_name,
                    "type": type(e).__name__,
                    "message": str(e),
                }
                return state

        return wrapper
    return decorator

def route_or_error(next_node: str):
    def router(state: ChatState):
        if state.get("error"):
            return "error_handler"
        return next_node
    return router