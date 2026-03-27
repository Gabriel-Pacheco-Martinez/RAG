"""
Author: Gabriel Pacheco
Date: February 2026
"""
# General
from colorama import Fore, Style

# Classes
from src.indexing.chunker import WebsiteChunker
from src.indexing.embedder import Embedder
from src.indexing.indexer import Indexer

# Configuration
from config.settings import settings
from config.settings import ASYNC_QDRANT_CLIENT
from config.settings import DENSE_MODEL
from config.settings import DENSE_TOKENIZER

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

async def run():
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
    metadata: dict =chunker.chunk_document(settings.WEBSITE_LOADED_FILE_PATH)
    chunks: dict = chunker.save_chunks(settings.WEBSITE_METADATA_FILE_PATH, metadata)
    metadata, chunks = chunker.get_chunks(settings.WEBSITE_METADATA_FILE_PATH)
    logger.info("✅ Successfull chunking")

    # =======
    # Embed the chunks
    embedder = Embedder(DENSE_MODEL, DENSE_TOKENIZER, settings.EMBEDDING_BATCH_SIZE)
    embeddings_chunks = embedder.embed_chunks(chunks)
    logger.info("✅ Successfull embedding")

    # =======
    # Index the embeddings with their metadata
    indexer = Indexer(ASYNC_QDRANT_CLIENT, settings.EMBEDDING_N_DIMENSIONS)
    await indexer.index_embeddings(metadata, embeddings_chunks)
    logger.info("✅ Successfull indexing")

    return f"Metadata saved in Qdrant sucessfully."
