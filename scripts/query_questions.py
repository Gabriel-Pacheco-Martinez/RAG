from src.data_pipeline.embedder import ChunkEmbedder
from src.retrieval.vector_searcher import FAISSSearcher
from src.generation.llm_client import LLM_Engine

from config.settings import FAISS_INDEX_PATH
from config.settings import FAISS_METADATA_PATH
from config.settings import CHUNK_METADATA_PATH

from config import load_config

def run(query):
    print("\n")
    print("=" * 60)
    print("🔎 Search Section:")
    print("=" * 60)

    # ======
    # Load configuration
    cfg = load_config()
    EMBEDDING_MODEL = cfg["EMBEDDING_MODEL"]
    EMBEDDING_BATCH_SIZE = cfg["EMBEDDING_BATCH_SIZE"]
    THRESHOLD = cfg["THRESHOLD"]
    TOP_K = cfg["TOP_K"]

    # =======
    # Embed the query
    embedder = ChunkEmbedder(model_name=EMBEDDING_MODEL, batch_size=EMBEDDING_BATCH_SIZE)
    embedding_query = embedder.embed_query(query)
    print("✅ Successfull embedding")
    
    # =======
    # Search embeddings
    searcher = FAISSSearcher(index_path=FAISS_INDEX_PATH, metadata_path=FAISS_METADATA_PATH)
    vectors = searcher.search(embedding_query, THRESHOLD, TOP_K)
    print("✅ Successfull search\n")

    # =======
    # Print results
    print("=" * 60)
    print("📄 Retrieved Context Chunks:")
    print("=" * 60)
    for i, v in enumerate(vectors, start=1):
        print(f"🔹 \033[34mResult {i}:\033[0m")
        print(f"   • Chunk ID   : {v['chunk_id']}")
        print(f"   • Similarity : {v['similarity']:.2f}")
        print(f"   • Text       : {v['text']}")

    # =======
    # Prompt generation and call llm
    print("\n")
    print("=" * 60)
    print("🧠 LLM Interaction:")
    print("=" * 60)

    llm = LLM_Engine(CHUNK_METADATA_PATH)
    context = llm.generate_context(vectors)
    llm_response = llm.prompt_llm(context, query)

if __name__ == "__main__":
    question = "Informacion relevante a banca joven. Tengo 18 años"
    # question = "Informacion relevante a banca senior."
    run(question)