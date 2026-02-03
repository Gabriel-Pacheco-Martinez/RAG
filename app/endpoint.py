from fastapi import FastAPI
from pydantic import BaseModel, Field, validator
from src import generate, intent
import uvicorn

from fastapi.responses import JSONResponse

app = FastAPI(title="BNB CHATBOT")

class GeneratorQueryRequest(BaseModel):
    mensaje: str

class QueryRequest(BaseModel):
    session_id: int
    mensaje: str


@app.post("/pregunta_generation")
def query_endpoint(request: GeneratorQueryRequest):
    llm_response = generate.run(request.mensaje)

    response_payload = {
        "mensaje": request.mensaje,
        "llm": llm_response
    }

    return JSONResponse(content=response_payload)


@app.post("/pregunta_intent")
def query_endpoint(request: QueryRequest):
    intention, system_response  = intent.run(request, "text")

    response_payload = {
        "mensaje": request.mensaje,
        "intencion del usuario": intention,
        "system response": system_response
    }

    return JSONResponse(content=response_payload)


def start_server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run("app.endpoint:app", host=host, port=port, reload=True)