# Server
import uvicorn 

# Models
from src.models.query import QueryRequest

# FastAPI
from fastapi.responses import JSONResponse
from fastapi import FastAPI, UploadFile, Form, File
app = FastAPI(title="BNB CHATBOT")

# LangGraph
from src import graph

@app.post("/conversation")
def query_endpoint(request: QueryRequest):
    response = graph.run(request)

    response_payload = {
        "mensaje": request.mensaje,
        "response": response
    }

    return JSONResponse(content=response_payload)

def start_server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run("app.endpoint:app", host=host, port=port, reload=True)