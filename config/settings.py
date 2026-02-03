import os 
import redis
from dotenv import load_dotenv
from colorama import Fore, Style

# Load .env secrets
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =====
# Redis communication
TTL_SECONDS = 900
REDIS_CLIENT = redis.StrictRedis(
    host="localhost",
    port=6379,          # Docker exposed port
    db=0,               # This goes from 0 to 15 
    decode_responses=True
)

# =====
# Constraints
MAX_AUDIO_SIZE = 200000
MAX_TEXT_SIZE = 75

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
PROMPTS_GENERATION_PATH = "src/generation/"
PROMPTS_INTENT_PATH = "src/intention/"
SCHEMAS_PATH = "schemas/"
