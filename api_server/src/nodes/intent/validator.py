# General
from typing import Tuple
from abc import ABC, abstractmethod

# Exceptions
from src.models.exceptions import ValidationError

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

class Validator(ABC):
    def __init__(self, message_data, format, max_size: int) -> None:
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
