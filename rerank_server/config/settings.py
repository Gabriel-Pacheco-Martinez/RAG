# Qdrant
from qdrant_client import AsyncQdrantClient

# HuggingFace
from sentence_transformers import CrossEncoder

# Configuration
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Load variables
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # RERANKER MODEL
    RERANKER_MODEL_NAME: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"


settings = Settings()

RERANKER_MODEL = CrossEncoder(settings.RERANKER_MODEL_NAME)
