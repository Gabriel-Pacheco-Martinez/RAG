from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    points: list[dict]