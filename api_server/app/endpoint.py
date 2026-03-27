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
from src.models.query import QueryRequest, SearchPayload

# FastAPI
from fastapi.responses import JSONResponse
from fastapi import FastAPI
from fastapi import UploadFile, Form, File
app = FastAPI(title="BNB CHATBOT")

# Classes
from src import graph
from src import index

# TODO: Delete
from src.nodes.generate.searcher import search

# Logging
logger = logging.getLogger('uvicorn.error')

@app.post("/conversation")
async def conversation_endpoint(request: QueryRequest):
    logger.info(Fore.GREEN + "="*50)
    logger.info(Fore.GREEN + "[🤖] Endpoint POST /conversation reached")
    logger.info(Fore.GREEN + "="*50 + Style.RESET_ALL)

    response = await graph.run(request)

    return JSONResponse(content=response)

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

    return JSONResponse(content=response)

@app.get("/index")
async def index_endpoint():
    logger.info(Fore.GREEN + "="*50)
    logger.info(Fore.GREEN + "[📚] Endpoint GET /index reached")
    logger.info(Fore.GREEN + "="*50 + Style.RESET_ALL)

    response = await index.run()

    response_payload = {
        "status": 200,
        "message": response,
        "data": {}
    }

    return JSONResponse(content=response_payload)

@app.get("/health")
async def health_check():
    logger.info(Fore.GREEN + "="*50)
    logger.info(Fore.GREEN + "[💚] Endpoint GET /health reached")
    logger.info(Fore.GREEN + "="*50 + Style.RESET_ALL)

    response_payload = {
        "staus": 200,
        "message": "🚀 BNB Chatbot API 'api_server' is up and running!",
        "data": {
            "service": "bnb-chatbot",
            "version": "1.0.0"
        }
    }

    return JSONResponse(content=response_payload)

@app.post("/search")
async def searching(payload: SearchPayload):
    results = await search(**payload.model_dump()) 
    dict_results = [result.model_dump() for result in results]
    return JSONResponse(content=dict_results)

def start_server(host: str = "0.0.0.0", port: int = 8000):
    # Uvicorn
    uvicorn.run(
        "app.endpoint:app", 
        host=host, 
        port=port, 
        reload=False,
        log_level="info",
        log_config="config/logconfig.json",
        workers=4
    )