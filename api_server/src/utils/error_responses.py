# Exceptions
from src.models.exceptions import ValidationError

def build_error_response(error: dict) -> str:
    error_type = error.get("type")
    if error_type == "ValidationError":
        return "Tu mensaje es muy largo, no puede ser procesado."
    elif error_type == "GuardingError":
        return "Mensaje invalido."
    elif error_type == "RateLimitError":
        return error.get("error", "Has alcanzado el límite de preguntas. Intenta de nuevo más tarde.")

    return "Lo siento, ocurrió un error procesando tu solicitud."

def get_error_status_code(error:dict) -> str:
    error_type = error.get("type")
    if error_type == "ValidationError":
        return 422
    elif error_type == "GuardingError":
        return 403
    elif error_type == "RateLimitError":
        return 429

    return 500