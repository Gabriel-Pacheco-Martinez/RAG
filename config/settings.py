"""
Here is settings.py I will include:
- API Keys
- Paths
- Flags for debug/production
- Database URLs
- Anything loaded from an .env file
"""

# ======
# Vector Database
FAISS_INDEX_PATH = "data/vector_db/faiss_index.bin"
FAISS_METADATA_PATH = "data/vector_db/faiss_metadata.json"

# =====
# Input data
ORIGINAL_DOCUMENTS_PATH = "data/raw/"
PROCESSED_DOCUMENTS_PATH = "data/processed/"
METADATA_PATH = "data/processed/metadata_new.json"

# =====
# Prompts path
PROMPTS_PATH = "src/generation/"
