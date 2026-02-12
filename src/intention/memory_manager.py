# from core.utils.redis import deserialize_session_data, serialize_session_data
# import json

# class MemoryManager():
#     def __init__(self, REDIS_CLIENT: object, TTL_SECONDS: int):
#         self.redis_client = REDIS_CLIENT
#         self.ttl_seconds = TTL_SECONDS

#     def review_response(self, intention_answer: dict) -> dict:
#         if intention_answer["confianza_en_la_intencion"] < 0.75:
#             intention_answer["intencion_actual"] = "menu"
#             return intention_answer

#         if intention_answer["intencion_actual"] == "nula":
#             intention_answer["intencion_actual"] = "menu"
#             return 
        
#         return intention_answer

#     def _process_qr_slots(self, slot_names: list, source_slots, session_data: dict):
#         status = "completo"

#         for slot in slot_names:
#             if not source_slots[slot]:
#                 session_data["slots_faltantes"].append(slot)
#                 session_data["slots"][slot] = ""
#                 status = "incompleto"
#             else:
#                 session_data["slots"][slot] = source_slots[slot]

#         return status

#     def update_session_data(self, intention_answer: dict, session_id: int, user_message_text: str, llm_answer: dict):
#         # Read session data
#         session_data = self.redis_client.hgetall(session_id)
#         session_data: dict = deserialize_session_data(session_data)

#         # Update intenciones
#         tmp_intencion = session_data["intencion_actual"]
#         session_data["intencion_previa"] = tmp_intencion
#         session_data["intencion_actual"] = intention_answer["intencion_actual"]

#         # Update confianza
#         session_data["confianza_en_la_intencion_actual"] = intention_answer["confianza_en_la_intencion"]

#         # Update historial de mensajes
#         historial_de_mensajes = session_data["historial_de_mensajes"]
#         historial_de_mensajes.append("Usuario:" + user_message_text)
        
#         if len(historial_de_mensajes) > 6:
#             historial_de_mensajes = historial_de_mensajes[-6:]

#         if llm_answer:
#             print("HELLO!!")
#             historial_de_mensajes.append("LLM:" + llm_answer["answer"])
#             if len(historial_de_mensajes) > 6:
#                 historial_de_mensajes = historial_de_mensajes[-6:]
#         session_data["historial_de_mensajes"] = json.dumps(historial_de_mensajes)

#         # Update context
#         if llm_answer:
#             session_data["context"] = llm_answer["context"]

#         # Update slots and status
#         intent = intention_answer["intencion_actual"]
#         session_data["slots_faltantes"] = []
#         if intent == "cobre con qr":
#             status_cobre = self._process_qr_slots(["monto", "destinatario"], intention_answer["slots_requeridos"], session_data)
#             # session_data["slots"]["rag_context"] = "false"
#             session_data["status"] = status_cobre

#         elif intent == "pague con qr":
#             status_pague = self._process_qr_slots(["monto", "destinatario"], intention_answer["slots_requeridos"], session_data)
#             # session_data["slots"]["rag_context"] = "false"
#             session_data["status"] = status_pague

#         elif intent == "preguntas":
#             # session_data["slots"]["rag_context"] = intention_answer["slots_requeridos"]["rag_context"]
#             session_data["status"] = "en proceso"
#         else:
#             # session_data["slots"]["rag_context"] = "false"
#             session_data["status"] = "completo"


#         # Update data on REDIS
#         session_data = serialize_session_data(session_data)
#         self.redis_client.hset(session_id, mapping=session_data)

#         # Reset TTL every time we update
#         self.redis_client.expire(session_id, self.ttl_seconds)

#         return session_data
    