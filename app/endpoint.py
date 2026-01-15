from fastapi import FastAPI
from pydantic import BaseModel, Field, validator
from scripts import query_questions
import uvicorn

from fastapi.responses import JSONResponse

app = FastAPI(title="RAG server")

class QueryRequest(BaseModel):
    pregunta: str

@app.post("/pregunta")
def query_endpoint(request: QueryRequest):
    llm_response = query_questions.run(request.pregunta)

    response_payload = {
        "pregunta": request.pregunta,
        **llm_response  # Unpack the dictionary
    }

    return JSONResponse(content=response_payload)

def start_server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run("app.endpoint:app", host=host, port=port, reload=True)