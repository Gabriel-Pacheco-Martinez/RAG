# General
from typing import Set, Any, Dict
from typing import Tuple
from pprint import pprint

# Created classes
from core.intention.validator import TextValidator, AudioValidator
from src.intention.converter import AudioConverter
from src.intention.intent_client import GeminiClient

# Configuration 
from config.settings import REDIS_CLIENT
from config.settings import REDIS_TTL_SECONDS
from config.settings import GEMINI_API_KEY
from config.settings import GROQ_API_KEY
from config.settings import MAX_TEXT_SIZE
from config.settings import MAX_AUDIO_SIZE
from config import load_config

def run(user_message_object: object, format: str) -> Tuple[str, str]:
    # =======
    # Load yaml configuration
    config = load_config() # Reads the YAML file and converts it into a dictionary
    GEMINI_MODEL: str = config["GEMINI_MODEL"]
    GROQ_MODEL: str = config["GROQ_MODEL"]


    # =======
    # Validate input
    if format == "text":
        validator = TextValidator(user_message_object.mensaje, format="text", max_size=MAX_TEXT_SIZE)
        user_message_text: str = validator.validate_input()
        print("✅ Successfull text validation") 
    elif format == "audio":
        validator = AudioValidator(user_message_object.mensaje, format="audio", max_size=MAX_AUDIO_SIZE)
        user_message_audio: Any = validator.validate_input()
        print("✅ Successfull audio validation") 

    # =======
    # Format input to text
    if format == "audio":
        converter = AudioConverter(GEMINI_MODEL, GEMINI_API_KEY)
        user_message_text: str = converter.convert_audio_to_text(user_message_audio)
        print("✅ Successfull audio to text conversion") 

