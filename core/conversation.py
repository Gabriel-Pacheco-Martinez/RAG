# General
import logging
from colorama import Fore, Style

# LangGraph
from langgraph.graph import StateGraph
from core.models.state import ChatState

# Nodes
from core.nodes.memoria.read import read_memory
from core.nodes.classify.classify import classify_query

# Configuration
logger = logging.getLogger(__name__)


def run(user_message: object) -> str:
    # Create the graph
    graph = StateGraph(ChatState)
    user_session_id = user_message.session_id
    user_message_text = user_message.mensaje

    # Add nodes
    graph.add_node("read_memory", read_memory)
    graph.add_node("classify_query", classify_query)

    # Add entry and finish nodes
    graph.set_entry_point("read_memory")
    graph.add_edge("read_memory", "classify_query")
    graph.set_finish_point("classify_query")

    # Compile the graph
    app = graph.compile()

    # Invoke the graph
    final_state = app.invoke({
        "user_session_id": user_session_id,
        "user_message": user_message_text,
    })

    return final_state

if __name__ == "__main__":
    run()