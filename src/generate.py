# General
import logging
import pprint
from colorama import Fore, Style

# Classes
from src.indexing.embedder import Embedder
from src.generation.searcher import FAISSSearcher, FAISSSeacherHierarchical
from src.generation.generation_client import LLM_Engine_PDFs, LLM_Engine_WEBSITEs

# Configuration
from config.settings import PDF_METADATA_FILE_PATH, WEBSITE_METADATA_FILE_PATH
from config.settings import QDRANT_CLIENT

from config import load_config
logger = logging.getLogger(__name__)

def run(query) -> dict:
    # =========
    # Logging
    print(Fore.GREEN + "="*50)
    print("[💼] GENERATION")
    print("="*50 + Style.RESET_ALL)

    # =========
    # Logging
    logger.info(Fore.GREEN + "="*50)
    logger.info("[💼] GENERATION")
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
    searcher = FAISSSeacherHierarchical(QDRANT_CLIENT, THRESHOLD, TOP_K)
    vectors: list[dict] = searcher.search(embedded_query)
    print("✅ Successfull search")

    # # =======
    # # Print results
    # logger.info(Fore.MAGENTA + "=" * 60 + Style.RESET_ALL)
    # logger.info(Fore.MAGENTA + "💼 Retrieved Context Chunks:" + Style.RESET_ALL)
    # logger.info(Fore.MAGENTA + "=" * 60 + Style.RESET_ALL)
    # for i, v in enumerate(vectors, start=1):
    #     logger.info(Fore.BLUE + f"Result {i}:" + Style.RESET_ALL)
    #     logger.info(f"   • Chunk ID   : {v['chunk_id']}")
    #     logger.info(f"   • Similarity : {v['similarity']:.2f}")
    #     logger.info(f"   • Text       : {v['text']}")
    # print("✅ Successfull retrieval")

    # # =======
    # # Prompt generation and call llm
    # llm = LLM_Engine_WEBSITEs(LLM_SOURCE, cfg, metadata_file_path=WEBSITE_METADATA_FILE_PATH)
    # context = llm.generate_context(vectors)
    # llm_response = llm.prompt_llm(query, context)

    # # ======
    # # Say something
    # return llm_response

if __name__ == "__main__":
    run("Informacion depositos a plazo fijo")