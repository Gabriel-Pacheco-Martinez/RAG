# General
from colorama import Fore, Style
from time import perf_counter

# LangGraph
from src.models.state import ChatState

# Qdrant
from qdrant_client.models import ScoredPoint

# Helpers
from src.utils.io import read_json

# Classes
from src.indexing.embedder import Embedder
from src.generation.searcher import Searcher
from src.generation.client import LLM_Engine

# Configuration
from config.settings import EMBEDDING_MODEL
from config.settings import EMBEDDING_BATCH_SIZE
from config.settings import RERANKER_MODEL
from config.settings import QDRANT_CLIENT
from config.settings import THRESHOLD
from config.settings import GROQ_GENERATOR_MODEL
from config.settings import GEMINI_GENERATOR_MODEL
from config.settings import LLM_SOURCE
from config.settings import WEBSITE_METADATA_FILE_PATH

def llm_rag_retrieval(state: ChatState):
    # Start timer
    state["start_time_1"] = perf_counter()

    # Query
    query = state["user_message"]

    # Embedd query
    embedder = Embedder(EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE)
    embedded_query = embedder.embed_query(query)

    # Search embeddings
    topic = state["topic"] # Select topic by classify
    searcher = Searcher(QDRANT_CLIENT, THRESHOLD, RERANKER_MODEL)
    vectors: list[ScoredPoint] = searcher.search(embedded_query, query, topic)
    state["document"] = vectors[0].payload.get('doc_titulo', '').upper()
    state["chapter"] = vectors[0].payload.get('cap_titulo', '').upper()

    # Load metadata
    textos = read_json(WEBSITE_METADATA_FILE_PATH)["textos"]

    # Prompt generation
    llm = LLM_Engine(LLM_SOURCE, GROQ_GENERATOR_MODEL, GEMINI_GENERATOR_MODEL)
    context = llm.generate_context(vectors, textos)

    # Update state
    state["context"] = context

    # Timer
    print(f"[RAG TIME:] {perf_counter() - state['start_time_1']:.4f}s")

    return state