from fastapi import FastAPI, UploadFile, Form, File
from pydantic import BaseModel
from pydantic import BaseModel, Field, validator
from core import graph
import uvicorn

from fastapi.responses import JSONResponse

app = FastAPI(title="BNB CHATBOT")

class GeneratorQueryRequest(BaseModel):
    mensaje: str

class QueryRequest(BaseModel):
    session_id: int
    mensaje: str


@app.post("/conversation")
def query_endpoint(request: QueryRequest):
    response = graph.run(request)

    response_payload = {
        "mensaje": request.mensaje,
        "response": response
    }

    return JSONResponse(content=response_payload)

# @app.post("/pregunta_generation")
# def query_endpoint(request: GeneratorQueryRequest):
#     llm_response = generate.run(request.mensaje)

#     response_payload = {
#         "mensaje": request.mensaje,
#         "llm": llm_response
#     }

#     return JSONResponse(content=response_payload)


# @app.post("/pregunta_intent")
# def query_endpoint(request: QueryRequest):
#     intention, system_response, memoria  = intent.run(request, "text")

#     response_payload = {
#         "mensaje": request.mensaje,
#         "system response": system_response,
#         "memoria": memoria,
#         "intencion del usuario": intention
#     }

#     return JSONResponse(content=response_payload)



def start_server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run("app.endpoint:app", host=host, port=port, reload=True)