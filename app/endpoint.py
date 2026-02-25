# Server
import uvicorn 

# Models
from src.models.query import QueryRequest

# FastAPI
from fastapi.responses import JSONResponse
from fastapi import FastAPI
from fastapi import UploadFile, Form, File
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

@app.post("/audio")
async def query_endpoint(TextChatbot: str = Form(None), AudioChatbot: UploadFile = File(None)):
    if AudioChatbot is not None:
        audio_bytes = await AudioChatbot.read()
        request = QueryRequest(session_id=10, mensaje=audio_bytes)
    if TextChatbot is not None:
        request = QueryRequest(session_id=10, mensaje=TextChatbot)

    response = graph.run(request)

    response_payload = {
        "response": response
    }

    return JSONResponse(content=response_payload)


def start_server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run("app.endpoint:app", host=host, port=port, reload=True)