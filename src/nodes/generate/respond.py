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
    # Prompt generation
    llm = LLM_Engine(LLM_SOURCE, GROQ_GENERATOR_MODEL, GEMINI_GENERATOR_MODEL)
    llm_response = llm.prompt_llm(state["user_message"], state["context"])

    # Update state
    state["llm_query_response"] = llm_response
    state["conversation_history"].append(f"User:{state['user_message']}")
    state["conversation_history"].append(f"System:{state['llm_query_response']}")

    print(state)

    # UPDATE FINAL STATE
    state["final_answer"] = {
        "topic": state["topic"],
        "context": state["llm_clarify_response"],
        "response": state["llm_query_response"],
        "context": state["context"]
    }

    return state
