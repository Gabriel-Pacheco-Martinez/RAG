# General
from typing import Tuple
from abc import ABC, abstractmethod
from colorama import Fore, Style

# Exceptions
from src.models.exceptions import ValidationError, RateLimitError

# Classes
from src.utils.limiter import rate_limiter

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

class Validator(ABC):
    def __init__(self, message_data: str, format: str, max_size: int) -> None:
        self.message_data = message_data
        self.format = format
        self.max_size = max_size

    @abstractmethod
    def validate_input(self) -> str:
        pass

class TextValidator(Validator):
    def validate_input(self) -> str:
        text_size = len(self.message_data)
        if text_size > self.max_size:
            logging.info(f"User message 'text' is too long: {text_size} characters")
            raise ValidationError("El mensaje es demasiado largo.")
        logging.info("User message 'text' is valid")
        return self.message_data

class AudioValidator(Validator):
    def validate_input(self):
        audio_size = len(self.message_data)
        if audio_size > self.max_size:
            logging.info(f"User message 'audio' is too long: {audio_size} bytes")
            raise ValidationError("El audio es demasiado largo.")
        logging.info("User message 'audio' is valid")
        return self.message_data

class RateLimitValidator(Validator):
    def __init__(self, session_id:str):
        self.session_id = session_id

    async def validate_input(self):
        result = await rate_limiter.is_allowed(self.session_id)
        if not result.allowed:
            logger.info(Fore.RED + f"Session {self.session_id} exceeded rate limit. Retry after {result.retry_after}s" + Style.RESET_ALL)
            raise RateLimitError(
                f"Has alcanzado el límite de preguntas por el momento. "
                f"Intenta de nuevo en {result.retry_after // 60} minutos."
            )
        logger.info(f"Session {self.session_id} rate limit OK — {result.remaining} requests remaining")