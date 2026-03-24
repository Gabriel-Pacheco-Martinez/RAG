# General
import logging
import inspect
import asyncio

# Classes
from src.models.state import ChatState

# Configuration
logger = logging.getLogger(__name__)

def safe_node(node_name: str):
    def decorator(func):
        async def wrapper(state: ChatState) -> ChatState:
            try:
                if inspect.iscoroutinefunction(func):
                    return await func(state)
                else:
                    return await asyncio.to_thread(func, state)

            except Exception as e:
                state["error_data"] = {
                    "node": node_name,
                    "type": type(e).__name__,
                    "error": str(e),
                }
                logger.exception(f"[❌] Error in node {node_name}")
                logger.error(f"Workflow failed: {e}")

                return state

        return wrapper
    return decorator

def route_or_error(next_node: str):
    def router(state: ChatState):
        if state.get("error_data"):
            return "error_handler"
        return next_node
    return router