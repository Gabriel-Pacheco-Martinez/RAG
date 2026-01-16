from src.data_pipeline.document_loader import PDFDocumentLoader
from src.data_pipeline.chunker import PDFDocumentChunker
from src.data_pipeline.embedder import ChunkEmbedder
from src.data_pipeline.indexer import FAISSIndexer

from config.settings import FAISS_INDEX_PATH
from config.settings import FAISS_METADATA_PATH
from config.settings import METADATA_PATH
from config.settings import DOCUMENTS_PATH

from config import load_config
import json

def run():
    print("=" * 60)
    print("💼 Ingestion Section:")
    print("=" * 60)

    # ======
    # Load configuration
    cfg = load_config()
    EMBEDDING_MODEL = cfg["EMBEDDING_MODEL"]
    EMBEDDING_BATCH_SIZE = cfg["EMBEDDING_BATCH_SIZE"]
    EMBEDDING_N_DIMENSIONS = cfg["EMBEDDING_N_DIMENSIONS"]

    # =======
    # Load the PDF document
    loader = PDFDocumentLoader(DOCUMENTS_PATH)
    documents_info = loader.load_documents()
    print("✅ Successfull loading")
    with open ("documents.json", "w", encoding="utf-8") as f:
        json.dump(documents_info, f, ensure_ascii=False, indent=4)
    
    # =======
    # Chunk the document
    chunker = PDFDocumentChunker(METADATA_PATH)
    chunks = chunker.chunk_document(documents_info)
    print("✅ Successfull chunking")

    # =======
    # Embed the chunks
    embedder = ChunkEmbedder(model_name=EMBEDDING_MODEL, batch_size=EMBEDDING_BATCH_SIZE)
    embeddings_chunks = embedder.embed_chunks(chunks)
    print("✅ Successfull embedding")

    # =======
    # Index the embeddings
    indexer = FAISSIndexer(dim=EMBEDDING_N_DIMENSIONS, index_path=FAISS_INDEX_PATH, metadata_path=FAISS_METADATA_PATH)
    indexer.index_embeddings(embeddings_chunks)
    print("✅ Successfull FAISS indexing")

if __name__ == "__main__":
    run()