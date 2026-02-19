# General
from colorama import Fore, Style

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

def use_rag(state: ChatState):
    # Query
    query = state["user_message"]

    # Embedd query
    embedder = Embedder(EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE)
    embedded_query = embedder.embed_query(query)

    # Search embeddings
    topic = state["topic"] # Select topic by classify
    searcher = Searcher(QDRANT_CLIENT, THRESHOLD, TOP_K)
    vector: list[dict] = searcher.search(embedded_query, query, topic)
    return vector # For testing

    # Prompt generation
    llm = LLM_Engine(LLM_SOURCE, GROQ_GENERATOR_MODEL, GEMINI_GENERATOR_MODEL)
    context = llm.generate_context(vector)

    # Update state
    state["context"] = context

    return state