# General
from colorama import Fore, Style

# Classes
from src.indexing.loader import PDFDocumentLoader
from src.indexing.chunker import WebsiteChunker
from src.indexing.embedder import Embedder
from src.indexing.indexer import Indexer

# Configuration
from config.settings import PDF_RAW_DOCS_PATH, PDF_LOADED_FILE_PATH, PDF_METADATA_FILE_PATH
from config.settings import WEBSITE_LOADED_FILE_PATH, WEBSITE_METADATA_FILE_PATH
from config.settings import QDRANT_CLIENT
from config.settings import EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE, EMBEDDING_N_DIMENSIONS

# Logging
import logging
logger = logging.getLogger(__name__)

def run():
    # =========
    # Printing
    print(Fore.GREEN + "="*50)
    print("[📚] INGESTION")
    print("="*50 + Style.RESET_ALL)

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
    embedder = Embedder(EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE)
    embeddings_chunks = embedder.embed_chunks(chunks)
    print("✅ Successfull embedding")

    # =======
    # Index the embeddings
    indexer = Indexer(QDRANT_CLIENT, EMBEDDING_N_DIMENSIONS)
    indexer.index_embeddings(metadata, embeddings_chunks)
    print("✅ Successfull indexing")

if __name__ == "__main__":
    run()