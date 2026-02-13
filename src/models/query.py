from pydantic import BaseModel

class QueryRequest(BaseModel):
    session_id: int
    mensaje: str