# General
from typing import Tuple
from abc import ABC, abstractmethod

# Exceptions
from src.models.exceptions import ValidationError

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
            raise ValidationError("El mensaje es demasiado largo.")
        return self.message_data

class AudioValidator(Validator):
    def validate_input(self):
        audio_size = len(self.message_data)
        if audio_size > self.max_size:
            raise ValidationError("El audio es demasiado largo.")
        return self.message_data
