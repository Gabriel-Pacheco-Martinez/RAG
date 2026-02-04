# General
from typing import Set, Any, Dict
from typing import Tuple
from pprint import pprint

# Created classes
from src.intention.session_manager import SessionManager
from src.intention.memory_manager import MemoryManager
from src.intention.validator import TextValidator, AudioValidator
from src.intention.converter import AudioConverter
from src.intention.intent_client import GeminiClient
from src import generate

# Configuration 
from config.settings import REDIS_CLIENT
from config.settings import TTL_SECONDS
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
    # Manage session
    session_manager = SessionManager(REDIS_CLIENT, TTL_SECONDS)
    memory = session_manager.get_or_create_session_data(user_message_object)

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

    # =======
    # Interaction with Intent LLM
    gemini_client = GeminiClient(GROQ_MODEL, GROQ_API_KEY)
    intention_answer: Dict[str, Any] = gemini_client.get_intent(user_message_text, memory)
    print(intention_answer)

    # =======
    # Manage memory
    response_manager = MemoryManager(REDIS_CLIENT, TTL_SECONDS)
    intention_answer = response_manager.review_response(intention_answer)
    session_data = response_manager.update_session_data(intention_answer, user_message_object.session_id, user_message_text)
    
    # =======
    # Interaction with Generation LLM if needed
    if intention_answer["intencion_actual"] == "preguntas":
        if intention_answer["slots_requeridos"]["rag_context"] == True:
            llm_answer = generate.run(user_message_text)
            return user_message_text, llm_answer
        else:
            return user_message_text, ""
