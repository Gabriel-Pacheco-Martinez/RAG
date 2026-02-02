import os 
from dotenv import load_dotenv
from colorama import Fore, Style

# Load .env secrets
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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
# Prompts path
PROMPTS_PATH = "src/generation/"
