from pydantic import BaseModel

class QueryRequest(BaseModel):
    session_id: int
    mensaje: str | bytes

class SearchPayload(BaseModel):
    state: dict
    query: str
    dense_embedding: list
    sparse_embedding: dict
    topic: str