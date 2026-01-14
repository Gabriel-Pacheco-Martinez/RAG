from src.data_pipeline.document_loader import PDFDocumentLoader
from src.data_pipeline.chunker import PDFDocumentChunker
from src.data_pipeline.embedder import ChunkEmbedder
from src.data_pipeline.indexer import FAISSIndexer

from config.settings import FAISS_INDEX_PATH
from config.settings import FAISS_METADATA_PATH

from config import load_config

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
    # # Load the PDF document
    # loader = PDFDocumentLoader("data/raw/documento.pdf")
    # text = loader.load_document()
    # print(text)
    
    # =======
    # Chunk the document
    chunker = PDFDocumentChunker(document_id=1042, author="BNB")
    chunks = chunker.chunk_document()
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