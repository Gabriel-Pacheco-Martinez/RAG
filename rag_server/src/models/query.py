from pydantic import BaseModel

class SparseEmbedding(BaseModel):
    indices: list[int]
    values: list[float]

class QueryRequest(BaseModel):
    query: str
    dense_embedding: list[float]
    sparse_embedding: SparseEmbedding
    topic: str