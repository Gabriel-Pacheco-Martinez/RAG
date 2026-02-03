from fastapi import FastAPI
from pydantic import BaseModel, Field, validator
from src import generate
import uvicorn

from fastapi.responses import JSONResponse

app = FastAPI(title="RAG server")

class QueryRequest(BaseModel):
    pregunta: str

@app.post("/pregunta")
def query_endpoint(request: QueryRequest):
    llm_response = generate.run(request.pregunta)

    response_payload = {
        "pregunta": request.pregunta,
        "llm": llm_response
    }

    return JSONResponse(content=response_payload)

def start_server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run("app.endpoint:app", host=host, port=port, reload=True)