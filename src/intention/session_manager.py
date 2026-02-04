import json
from src.utils.redis import deserialize_session_data

class SessionManager():
    def __init__(self, REDIS_CLIENT: object, TTL_SECONDS: int):
        self.redis_client = REDIS_CLIENT
        self.ttl_seconds = TTL_SECONDS

    def get_or_create_session_data(self, user_message_object: object):
        session_data = self.redis_client.hgetall(user_message_object.session_id)
        if not session_data:
            # Crear sesion.
            self.redis_client.hset(user_message_object.session_id, mapping={
                "intencion_previa": "",
                "intencion_actual": "desconocida",
                "confianza_en_la_intencion_actual": 0.0,
                "status": "empezando",
                "slots": json.dumps({}),
                "slots_faltantes": json.dumps([]),
                "historial_de_mensajes": json.dumps([]),
                "context": ""
            })

            # Set TTL
            self.redis_client.expire(user_message_object.session_id, self.ttl_seconds)  

            # Return session data
            session_data = self.redis_client.hgetall(user_message_object.session_id) #Refetch
            deserialize_session_data(session_data)
            return session_data
        else:
            # Return session data
            deserialize_session_data(session_data)
            return session_data