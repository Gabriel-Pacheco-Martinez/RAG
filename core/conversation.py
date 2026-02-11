# General
import logging
from colorama import Fore, Style

# LangGraph
from langgraph.graph import StateGraph
from core.models.lang import ChatState

# Nodes
from core.nodes.classification.classification import topic_classification

# Configuration
from config import load_config
logger = logging.getLogger(__name__)


def run(request: object) -> str:
    
    graph = StateGraph(ChatState)

    # graph.add_node("load_state", load_state_from_redis)

    graph.add_node("topic_classification", topic_classification)

    # graph.add_node("rewrite_query", rewrite_query)

    # graph.add_node("decide_rag", decide_rag_vs_memory)

    # graph.add_node("retrieve", retrieve_documents)
    # graph.add_node("rerank", cross_encoder_rerank)

    # graph.add_node("confidence_gate", pre_answer_confidence_gate)

    # graph.add_node("build_prompt", build_prompt)
    # graph.add_node("answer", llm_answer)

    # graph.add_node("save_state", save_state_to_redis)
