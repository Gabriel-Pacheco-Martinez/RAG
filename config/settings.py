# General
import os 
from colorama import Fore, Style

# Redis & Qdrant
import redis
from qdrant_client import QdrantClient

# Langchain
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env secrets
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =====
# Redis communication
REDIS_TTL_SECONDS = 900
REDIS_CLIENT = redis.StrictRedis(
    host="localhost",
    port=6379,          # Docker exposed port
    db=0,               # This goes from 0 to 15 
    decode_responses=True
)

# =====
# Qdrant client
QDRANT_CLIENT = QdrantClient(
    url="http://localhost:6333",  # Docker exposed port
)
TOP_K = 5
THRESHOLD = 0.3

# =====
# LLM Models
LLM_SOURCE = "groq"
GROQ_GENERATOR_MODEL = ChatGroq(model="llama-3.1-8b-instant", temperature=0, api_key=GROQ_API_KEY)
GEMINI_GENERATOR_MODEL = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0, google_api_key=GEMINI_API_KEY)
OLLAMA_GENERATOR_MODEL = ChatOllama(model="qwen3:8b", temperature=0)
GEMINI_MULTIMODAL_MODEL = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=GEMINI_API_KEY)

# =====
# Embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_BATCH_SIZE = 16
EMBEDDING_N_DIMENSIONS = 384

# =====
# Constraints
MAX_AUDIO_SIZE = 200000
MAX_TEXT_SIZE = 75
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

# =====
# LOGS
LOGS_PATH = "logs/"
LOGS_FILE = "logs/app.log"

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
