import json
from typing import Any

def deserialize_session_data(session_data: dict):
    session_data["confianza_en_la_intencion_actual"] = float(session_data["confianza_en_la_intencion_actual"])
    session_data["slots"] = json.loads(session_data["slots"])
    session_data["slots_faltantes"] = json.loads(session_data["slots_faltantes"])
    session_data["historial_de_mensajes"] = json.loads(session_data["historial_de_mensajes"])
    return session_data

def serialize_session_data(session_data: dict[str,Any]) -> dict[str,str]:
    serialized = {}
    for key, value in session_data.items():
        if isinstance(value, (dict, list)):
            serialized[key] = json.dumps(value)
        else:
            serialized[key] = str(value)
    return serialized