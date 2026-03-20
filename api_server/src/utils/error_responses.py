# Exceptions
from src.models.exceptions import ValidationError

def build_error_response(error: dict) -> str:
    error_type = error.get("type")
    if error_type == "ValidationError":
        return "Tu mensaje es muy largo, no puede ser procesado."
    elif error_type == "GuardingError":
        return "Mensaje invalido."

    return "Lo siento, ocurrió un error procesando tu solicitud."

def get_error_status_code(error:dict) -> str:
    error_type = error.get("type")
    if error_type == "ValidationError":
        return 422
    elif error_type == "GuardingError":
        return 403

    return 500