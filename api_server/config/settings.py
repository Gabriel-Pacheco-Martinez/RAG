# General
import os 
from colorama import Fore, Style

# Redis & Qdrant
import redis
from qdrant_client import AsyncQdrantClient

# Langchain
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# HuggingFace
from sentence_transformers import CrossEncoder
from transformers import AutoModel, AutoTokenizer, AutoModelForSequenceClassification

# Fastembed
from fastembed import SparseTextEmbedding

# Enums
from config.enums import LLMSource
from config.enums import GUARDSource

# Load .env secrets
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =====
# Rag Server communication
RAG_SERVER_URL = "http://nginx:8080"      # Docker
# RAG_SERVER_URL = "http://localhost:8002"    # Localhost

# =====
# Redis communication
REDIS_TTL_SECONDS = 900
REDIS_CLIENT = redis.StrictRedis(
    host="redis",       # Docker exposed
    # host="localhost",       # Localhost
    port=6379,          
    db=0,               # This goes from 0 to 15 
    decode_responses=True
)

# =====
# Qdrant client
ASYNC_QDRANT_CLIENT = AsyncQdrantClient(
    url="http://qdrant:6333",  # Docker exposed port
    # url="http://localhost:6333",  # Localhost port
)
TOP_K_DENSE = 8
TOP_K_SPARSE = 8
LIMIT_K_HYBRID = 5

# =====
# LLM Models
LLM_SOURCE = LLMSource.GROQ
GROQ_GENERATOR_MODEL = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0, api_key=GROQ_API_KEY)
GEMINI_GENERATOR_MODEL = ChatGoogleGenerativeAI(model="gemma-3-1b-it", temperature=0, google_api_key=GEMINI_API_KEY, convert_system_message_to_human=True)
OLLAMA_GENERATOR_MODEL = ChatOllama(model="llama3:8b", temperature=0, base_url="http://host.docker.internal:11434")

# =====
# Audio convertion model
GEMINI_MULTIMODAL_MODEL = "gemini-2.5-flash" # This will be called without LangChain

# =====
# Guarding model
GUARD_SOURCE = GUARDSource.HUGGING_FACE
GUARD_PROBABILITY_THRESHOLD = 0.2
GROQ_PROMPT_GUARD_MODEL = ChatGroq(model="meta-llama/llama-prompt-guard-2-86m", api_key=GROQ_API_KEY, temperature=0)
try:
    HF_PROMPT_GUARD_TOKENIZER = AutoTokenizer.from_pretrained("meta-llama/Llama-Prompt-Guard-2-86M")
    HF_PROMPT_GUARD_MODEL = AutoModelForSequenceClassification.from_pretrained("meta-llama/Llama-Prompt-Guard-2-86M")
except Exception as e:
    raise Exception (f"Error loading HuggingFace guarding models: {e}")

# =====
# Embeddings
EMBEDDING_BATCH_SIZE = 16
EMBEDDING_N_DIMENSIONS = 384
try:
    DENSE_MODEL = AutoModel.from_pretrained(f'sentence-transformers/all-MiniLM-L6-v2')
    DENSE_TOKENIZER = AutoTokenizer.from_pretrained(f'sentence-transformers/all-MiniLM-L6-v2')
    RERANKER_MODEL = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
except Exception as e:
    raise Exception(f"Error loading HuggingFace models and tokenizers: {e}")
try:
    SPARSE_MODEL = SparseTextEmbedding("Qdrant/bm25")
except Exception as e:
    raise Exception(f"Error loading Fastembed embedding bm25 library: {e}")

# =====
# Constraints
MAX_AUDIO_SIZE = 60000 #60KB
MAX_TEXT_SIZE = 150 #150 characters
MAX_MESSAGE_HISTORY_MEMORY = 6

# =====
# WEBSITE DATA: needs file path as single file
WEBSITE_LOADED_FILE_PATH = "data/loaded/website/website_loaded.json" 
WEBSITE_METADATA_FILE_PATH = "data/metadata/website/website_metadata.json"

# =====
# PDF DATA: needs folder path as multiple files
PDF_RAW_DOCS_PATH = "data/raw/pdfs/"
PDF_LOADED_FILE_PATH = "data/loaded/pdfs/pdf_loaded.json"
PDF_METADATA_FILE_PATH = "data/metadata/pdfs/pdf_metadata.json"

# ======
# Vector Database
FAISS_INDEX_PATH = "vector_db/faiss_index.bin"
FAISS_METADATA_PATH = "vector_db/faiss_metadata.json"

# =====
# Prompts and schemas path
PROMPTS_GENERATION_PATH = "core/generation/"
PROMPTS_INTENT_PATH = "core/intention/"
PROMPTS_PATH = "prompts/"
SCHEMAS_PATH = "schemas/"
