# General
from time import perf_counter

# LangGraph
from src.models.state import ChatState

# Classes
from src.indexing.embedder import Embedder
from src.generation.searcher import Searcher
from src.generation.client import LLM_Engine

# Configuration
from config.settings import EMBEDDING_MODEL
from config.settings import EMBEDDING_BATCH_SIZE
from config.settings import QDRANT_CLIENT
from config.settings import THRESHOLD
from config.settings import TOP_K
from config.settings import GROQ_GENERATOR_MODEL
from config.settings import GEMINI_GENERATOR_MODEL
from config.settings import LLM_SOURCE


def respond_query(state: ChatState) -> dict:
    # Start timer
    state["start_time_2"] = perf_counter()

    # Prompt generation
    llm = LLM_Engine(LLM_SOURCE, GROQ_GENERATOR_MODEL, GEMINI_GENERATOR_MODEL)
    llm_response = llm.prompt_llm(state["user_message"], state["context"])

    # Update state
    state["llm_query_response"] = f"""
        Informacion obtenida de la sección {state["document"]} del capítulo {state["chapter"]}:
        {llm_response}
        """
    
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

    # Say something
    print("🦺 GENERATION LLM: DONE")
    print(f"[LLM CALL:] {perf_counter() - state['start_time_2']:.4f}s")

    return state
