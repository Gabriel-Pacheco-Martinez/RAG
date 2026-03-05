"""
Author: Gabriel Pacheco
Date: February 2026
"""
# General
from colorama import Fore, Style
import logging

# Server
import uvicorn 

# Models
from src.models.query import QueryRequest

# FastAPI
from fastapi.responses import JSONResponse
from fastapi import FastAPI
from fastapi import UploadFile, Form, File
app = FastAPI(title="BNB CHATBOT")

# Classes
from src import graph
from src import index

# Logging
logger = logging.getLogger('uvicorn.error')

@app.post("/conversation")
async def conversation_endpoint(request: QueryRequest):
    logger.info(Fore.GREEN + "="*50)
    logger.info(Fore.GREEN + "[🤖] Endpoint POST /conversation reached")
    logger.info(Fore.GREEN + "="*50 + Style.RESET_ALL)

    response = await graph.run(request)

    response_payload = {
        "mensaje": request.mensaje,
        "response": response
    }

    return JSONResponse(content=response_payload)

@app.post("/audio")
async def audio_endpoint(TextChatbot: str = Form(None), AudioChatbot: UploadFile = File(None)):
    logger.info(Fore.GREEN + "="*50)
    logger.info(Fore.GREEN + "[🤖] Endpoint POST /audio reached")
    logger.info(Fore.GREEN + "="*50 + Style.RESET_ALL)

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

@app.get("/index")
def index_endpoint():
    logger.info(Fore.GREEN + "="*50)
    logger.info(Fore.GREEN + "[📚] Endpoint GET /index reached")
    logger.info(Fore.GREEN + "="*50 + Style.RESET_ALL)

    response =index.run()

    response_payload = {
        "response": "Success: " + response
    }

    return JSONResponse(content=response_payload)

def start_server(host: str = "0.0.0.0", port: int = 8000):
    # Uvicorn
    uvicorn.run(
        "app.endpoint:app", 
        host=host, 
        port=port, 
        reload=True, # This has to be false for logs to be saved to file
        log_level="info",
        log_config="config/logconfig.json",
        workers=1
    )