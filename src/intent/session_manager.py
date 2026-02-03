import json

class SessionManager():
    def __init__(self, REDIS_CLIENT: object, TTL_SECONDS: int):
        self.redis_client = REDIS_CLIENT
        self.ttl_seconds = TTL_SECONDS

    def get_or_create_session_data(self, user_message: object):
        session_data = self.redis_client.hgetall(user_message.session_id)
        if not session_data:
            # Crear sesion.
            self.redis_client.hset(user_message.session_id, mapping={
                "intencion_actual": "desconocida",
                "confianza_en_la_intencion": 0.0,
                "status": "por empezar",
                "slots": json.dumps({}), #redis can't handle python objects
                "slots_faltantes": json.dumps(["todos"]),
                "historial_de_mensajes": json.dumps([]),
            })

            # Set TTL
            self.redis_client.expire(user_message.session_id, self.ttl_seconds)
            return session_data
        else:
            # Already exists — Redis stores everything as strings
            # If you want Python objects for slots & historial, deserialize them
            if "slots" in session_data:
                session_data["slots"] = json.loads(session_data["slots"])
            if "historial_de_mensajes" in session_data:
                session_data["historial_de_mensajes"] = json.loads(session_data["historial_de_mensajes"])

            return session_data  # return the map retrieved from Redis


    def update_session_data(self, user_message: object, new_fields: dict):
        """
        Update existing session data or create it if missing.
        new_fields: dictionary of fields to add/update in the hash
        """
        # Add or update hash fields
        self.redis_client.hset(user_message.session_id, mapping=new_fields)

        # Reset TTL every time we update
        self.redis_client.expire(user_message.session_id, self.ttl_seconds)

        return "Sesion de datos actualizada"