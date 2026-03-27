# Qdrant
from qdrant_client import AsyncQdrantClient

# HuggingFace
from sentence_transformers import CrossEncoder

# =====
# Qdrant client
ASYNC_QDRANT_CLIENT = AsyncQdrantClient(
    url="http://qdrant:6333",  # Docker exposed port
    # url="http://localhost:6333",  # Localhost port
)
TOP_K_DENSE = 8
TOP_K_SPARSE = 8
LIMIT_N_HYBRID_CAPS = 3
LIMIT_N_HYBRID_TEXT = 4

# =====
# Embeddings
RERANKER_MODEL = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
# RERANKER_MODEL = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-2-v2")