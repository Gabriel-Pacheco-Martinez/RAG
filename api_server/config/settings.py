# General
import os 
from colorama import Fore, Style

# Redis & Qdrant
import redis
from redis import asyncio as aioredis
from qdrant_client import AsyncQdrantClient

# Langchain
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# HuggingFace
from sentence_transformers import CrossEncoder
from transformers import AutoModel
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification

# Fastembed
from fastembed import SparseTextEmbedding

# Enums
from config.enums import LLMSource
from config.enums import GUARDSource

# Configuration
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Load variables
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Secrets
    GEMINI_API_KEY: str = "GEMINI_API_KEY"
    GROQ_API_KEY: str = "GROQ_API_KEY"

    # NGINX
    NGINX_URL: str = "http://nginx:8080"

    # REDIS
    REDIS_HOST: str = "redis"  # Docker exposed
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_DECODE_RESPONSES: bool = True
    REDIS_TTL_SECONDS: int = 900

    # QDRANT
    QDRANT_URL: str = "http://qdrant:6333"  # Docker exposed
    TOP_K_DENSE: int = 8
    TOP_K_SPARSE: int = 8
    LIMIT_N_HYBRID_CAPS: int = 3
    LIMIT_N_HYBRID_TEXT: int = 4

    # EMBEDDINGS
    DENSE_EMBEDDER: str = "sentence-transformers/all-MiniLM-L6-v2"
    SPARSE_EMBEDDER: str = "Qdrant/bm25"
    EMBEDDING_BATCH_SIZE: int = 16
    EMBEDDING_N_DIMENSIONS: int = 384

    # CONSTRAINTS
    MAX_AUDIO_SIZE: int = 60000      # 60KB
    MAX_TEXT_SIZE: int = 150         # 150 characters
    MAX_MESSAGE_HISTORY_MEMORY: int = 6

    # MODEL SOURCES
    LLM_SOURCE: LLMSource = LLMSource.GROQ
    GUARD_SOURCE: GUARDSource = GUARDSource.HUGGING_FACE

    # OLLAMA
    OLLAMA_HOST: str = "http://host.docker.internal:11434"

    # LLMs
    GROQ_LLM: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    GEMINI_LLM: str = "gemma-3-1b-it"
    OLLAMA_LLM: str = "llama3:8b"
    
    # MULTIMODAL
    GEMINI_MULTIMODAL: str = "gemini-2.5-flash"

    # GUARD
    GUARD_PROBABILITY_THRESHOLD: float = 0.2
    GROQ_PROMPT_GUARD: str = "meta-llama/llama-prompt-guard-2-86m"
    HF_PROMPT_GUARD: str = "meta-llama/Llama-Prompt-Guard-2-86M"

    # WEBSITE DATA
    WEBSITE_LOADED_FILE_PATH: str = "data/loaded/website/website_loaded.json" 
    WEBSITE_METADATA_FILE_PATH: str = "data/metadata/website/website_metadata.json"

    # PROMPTS AND SCHEMAS
    PROMPTS_PATH: str = "prompts/"
    SCHEMAS_PATH: str = "schemas/"


settings = Settings()

REDIS_CLIENT = aioredis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=settings.REDIS_DECODE_RESPONSES
)

ASYNC_QDRANT_CLIENT = AsyncQdrantClient(
    url=settings.QDRANT_URL 
)

GEMINI_MULTIMODAL_MODEL = settings.GEMINI_MULTIMODAL # This will be used without langchain

GROQ_GENERATOR_MODEL = ChatGroq(
    model=settings.GROQ_LLM, 
    temperature=0, 
    api_key=settings.GROQ_API_KEY
)

GEMINI_GENERATOR_MODEL = ChatGoogleGenerativeAI(
    model=settings.GEMINI_LLM, 
    temperature=0, 
    google_api_key=settings.GEMINI_API_KEY, 
    convert_system_message_to_human=True
)

OLLAMA_GENERATOR_MODEL = ChatOllama(
    model=settings.OLLAMA_LLM, 
    temperature=0, 
    base_url=settings.OLLAMA_HOST
)

GROQ_PROMPT_GUARD_MODEL = ChatGroq(
    model=settings.GROQ_PROMPT_GUARD, 
    api_key=settings.GROQ_API_KEY, 
    temperature=0
)
try:
    HF_PROMPT_GUARD_TOKENIZER = AutoTokenizer.from_pretrained(settings.HF_PROMPT_GUARD)
    HF_PROMPT_GUARD_MODEL = AutoModelForSequenceClassification.from_pretrained(settings.HF_PROMPT_GUARD)
except Exception as e:
    raise Exception (f"Error loading HuggingFace guarding models: {e}")

try:
    DENSE_MODEL = AutoModel.from_pretrained(settings.DENSE_EMBEDDER)
    DENSE_TOKENIZER = AutoTokenizer.from_pretrained(settings.DENSE_EMBEDDER)
except Exception as e:
    raise Exception(f"Error loading HuggingFace models and tokenizers: {e}")

try:
    SPARSE_MODEL = SparseTextEmbedding(settings.SPARSE_EMBEDDER)
except Exception as e:
    raise Exception(f"Error loading Fastembed embedding bm25 library: {e}")


