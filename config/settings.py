"""
Here is settings.py I will include:
- API Keys
- Paths
- Flags for debug/production
- Database URLs
- Anything loaded from an .env file
"""

# ======
# Paths
FAISS_INDEX_PATH = "data/vector_db/faiss_index.bin"
FAISS_METADATA_PATH = "data/vector_db/faiss_metadata.json"
CHUNK_METADATA_PATH = "data/processed/metadata.json"
PROMPTS_PATH = "src/generation/"
