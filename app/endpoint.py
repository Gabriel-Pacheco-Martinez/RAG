from fastapi import FastAPI
from pydantic import BaseModel, Field, validator
from scripts import query_questions
import uvicorn

app = FastAPI(title="RAG server")

class QueryRequest(BaseModel):
    pregunta: str = Field(..., min_length=1, max_length=500, description="The question to query the RAG system")

    @validator("pregunta")
    def no_whitespace_only(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace")
        return v

@app.post("/pregunta")
def query_endpoint(request: QueryRequest):
    answer = query_questions.run(request.pregunta)
    return {"pregunta": request.pregunta, "respuesta": answer}

def start_server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run("app.endpoint:app", host=host, port=port, reload=True)