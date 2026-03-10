# Qdrant
from qdrant_client import AsyncQdrantClient

# HuggingFace
from sentence_transformers import CrossEncoder

# =====
# Qdrant client
ASYNC_QDRANT_CLIENT = AsyncQdrantClient(
    # url="http://qdrant:6333",  # Docker exposed port
    url="http://localhost:6333",  # Localhost port
)
TOP_K_DENSE = 8
TOP_K_SPARSE = 8
LIMIT_K_HYBRID = 5

# =====
# Embeddings
RERANKER_MODEL = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")