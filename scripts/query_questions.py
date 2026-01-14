import json
import yaml

from src.data_pipeline.document_loader import PDFDocumentLoader
from src.data_pipeline.chunker import PDFDocumentChunker
from src.data_pipeline.embedder import ChunkEmbedder
from src.data_pipeline.indexer import FAISSIndexer
from src.retreival.vector_searcher import FAISSSearcher
from pathlib import Path

from config.settings import FAISS_INDEX_PATH
from config.settings import FAISS_METADATA_PATH

from config import load_config

if __name__ == "__main__":
    # Load configuration
    cfg = load_config()
    EMBEDDING_MODEL = cfg["EMBEDDING_MODEL"]
    EMBEDDING_BATCH_SIZE = cfg["EMBEDDING_BATCH_SIZE"]
    EMBEDDING_N_DIMENSIONS = cfg["EMBEDDING_N_DIMENSIONS"]

    # query = "Información sobre la banca joven?"
    # query_embedding = embedder.embed_query(query)

    # print(query_embedding.shape)

    # searcher = FAISSSearcher(index_path=FAISS_INDEX_PATH, metadata_path=FAISS_METADATA_PATH)
    # results = searcher.search(query_embedding, top_k=2)
    # print(results)