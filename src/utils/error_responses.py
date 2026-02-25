# Exceptions
from src.models.exceptions import ValidationError

def build_error_response(error: dict) -> str:
    error_type = error.get("type")
    
    if error_type == "ValidationError":
        return "Tu mensaje es muy largo, no puede ser procesado."

    return (
        "Lo siento, ocurrió un error procesando tu solicitud. "
        "Por favor intenta nuevamente."
    )
    