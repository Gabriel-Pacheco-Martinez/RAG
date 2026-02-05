# General
import logging
from colorama import Fore, Style

# Classes
from src.indexing.loader import PDFDocumentLoader
from src.indexing.chunker import WebsiteChunker, PDFChunker
from src.indexing.embedder import Embedder
from src.indexing.indexer import FAISSIndexer

# Configuration
from config.settings import PDF_RAW_DOCS_PATH, PDF_LOADED_FILE_PATH, PDF_METADATA_FILE_PATH
from config.settings import WEBSITE_LOADED_FILE_PATH, WEBSITE_METADATA_FILE_PATH
from config.settings import FAISS_INDEX_PATH, FAISS_METADATA_PATH

from config import load_config
logger = logging.getLogger(__name__)

def run():
    # =========
    # Logging
    print(Fore.GREEN + "="*50)
    print("[💼] ESTAS EN RAG")
    print("="*50 + Style.RESET_ALL)

    # =========
    # Logging
    logger.info(Fore.GREEN + "="*50)
    logger.info("[💼] INGESTION")
    logger.info("="*50 + Style.RESET_ALL)

    # ======
    # Load configuration
    cfg = load_config()
    EMBEDDING_MODEL = cfg["EMBEDDING_MODEL"]
    EMBEDDING_BATCH_SIZE = cfg["EMBEDDING_BATCH_SIZE"]
    EMBEDDING_N_DIMENSIONS = cfg["EMBEDDING_N_DIMENSIONS"]

    # # =======
    # # Load the PDF Document
    # loader = PDFDocumentLoader(PDF_RAW_DOCS_PATH, PDF_LOADED_FILE_PATH)
    # documents_info = loader.load_documents()
    # print("✅ Successfull loading")

    # # =======
    # # Chunk the PDF document
    # chunker = PDFChunker()
    # metadata = chunker.chunk_document(documents_info)
    # chunks = chunker.get_and_save_chunks(PDF_METADATA_FILE_PATH, metadata)
    # print("✅ Successfull chunking")

    # =======
    # Chunk WEBSITE document
    chunker: object = WebsiteChunker()
    metadata: map =chunker.chunk_document(WEBSITE_LOADED_FILE_PATH)
    chunks: map = chunker.get_and_save_chunks(WEBSITE_METADATA_FILE_PATH, metadata) 
    print("✅ Successfull chunking")

    # =======
    # Embed the chunks
    embedder = Embedder(model_name=EMBEDDING_MODEL, batch_size=EMBEDDING_BATCH_SIZE)
    embeddings_chunks = embedder.embed_chunks(chunks)
    print("✅ Successfull embedding")

    # =======
    # Index the embeddings
    indexer = FAISSIndexer(dim=EMBEDDING_N_DIMENSIONS, index_path=FAISS_INDEX_PATH, metadata_path=FAISS_METADATA_PATH)
    indexer.index_embeddings(embeddings_chunks)
    print("✅ Successfull FAISS indexing")

if __name__ == "__main__":
    run()