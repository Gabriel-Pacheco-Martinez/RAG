import json
from typing import Any

def deserialize_session_data(session_data: dict):
    session_data["topic_previous"] = session_data["topic_previous"]
    session_data["conversation_history"] = json.loads(session_data["conversation_history"])
    session_data["context"] = session_data["context"] 
    return session_data

def serialize_session_data(session_data: dict[str,Any]) -> dict[str,str]:
    serialized = {}
    for key, value in session_data.items():
        if isinstance(value, (dict, list)):
            serialized[key] = json.dumps(value)
        else:
            serialized[key] = str(value)
    return serialized