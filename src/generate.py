# General
import logging
import pprint
from colorama import Fore, Style

# Classes
from src.indexing.embedder import Embedder
from src.generation.searcher import Searcher
from src.generation.generation_client import LLM_Engine

# Configuration
from config.settings import QDRANT_CLIENT

from config import load_config
logger = logging.getLogger(__name__)

def run(query) -> dict:
    # =========
    # Printing
    print(Fore.GREEN + "="*50)
    print("[⚙️ ] GENERATION")
    print("="*50 + Style.RESET_ALL)

    # =========
    # Logging
    logger.info(Fore.GREEN + "="*50)
    logger.info("[⚙️] GENERATION")
    logger.info("="*50 + Style.RESET_ALL)

    # ======
    # Load configuration
    cfg = load_config()
    EMBEDDING_MODEL = cfg["EMBEDDING_MODEL"]
    EMBEDDING_BATCH_SIZE = cfg["EMBEDDING_BATCH_SIZE"]
    THRESHOLD = cfg["THRESHOLD"]
    TOP_K = cfg["TOP_K"]
    LLM_SOURCE = cfg["LLM_SOURCE"]

    # =======
    # Embed the query
    embedder = Embedder(model_name=EMBEDDING_MODEL, batch_size=EMBEDDING_BATCH_SIZE)
    embedded_query = embedder.embed_query(query)
    print("✅ Successfull embedding of query")

    # =======
    # Search embeddings
    searcher = Searcher(QDRANT_CLIENT, THRESHOLD, TOP_K)
    vector: list[dict] = searcher.search(embedded_query)
    print("✅ Successfull search")

    # =======
    # Prompt generation and call llm
    llm = LLM_Engine(LLM_SOURCE, cfg)
    context = llm.generate_context(vector)
    llm_response = llm.prompt_llm(query, context)

    # ======
    # Say something
    return llm_response

if __name__ == "__main__":
    run("Beneficios credito vehiculo usado")