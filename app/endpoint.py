"""
Author: Gabriel Pacheco
Date: February 2026
"""
# General
from colorama import Fore, Style
from pathlib import Path
import logging
import logging.config

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

# Logging
logger = logging.getLogger('uvicorn.error')

@app.post("/conversation")
def query_endpoint(request: QueryRequest):
    logger.info(Fore.GREEN + "="*50)
    logger.info(Fore.GREEN + "[🤖] Endpoint POST /conversation reached")
    logger.info(Fore.GREEN + "="*50 + Style.RESET_ALL)

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
    # Uvicorn
    uvicorn.run(
        "app.endpoint:app", 
        host=host, 
        port=port, 
        reload=True, 
        log_level="info"
    )