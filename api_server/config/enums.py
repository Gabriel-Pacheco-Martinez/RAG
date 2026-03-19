from enum import Enum

class LLMSource(str, Enum):
    GROQ = "groq"
    OLLAMA = "ollama"
    GOOGLE = "google"

class GUARDSource(str, Enum):
    GROQ = "groq"
    HUGGING_FACE = "huggingface"