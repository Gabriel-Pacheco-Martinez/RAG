from typing import Tuple
from abc import ABC, abstractmethod

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
        if text_size > self.max_size: # This needs to raise an Exception I think
            return "El mensaje es demasiado largo: {text_size} bytes (máx {self.max_size} bytes)"
        return self.message_data

class AudioValidator(Validator):
    def validate_input(self):
        audio_size = len(self.message_data)
        if audio_size > self.max_size: # This needs to raise an Exception I think
            return "El audio es demasiado largo: {audio_size} bytes (máx {self.max_size} bytes)"
        return self.message_data
