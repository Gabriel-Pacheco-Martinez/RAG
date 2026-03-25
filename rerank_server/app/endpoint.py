"""
Author: Gabriel Pacheco
Date: February 2026
"""
# General
from contextlib import asynccontextmanager
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

# Classes
from src import rerank

# Logging
logger = logging.getLogger('uvicorn.error')

app = FastAPI(title="BNB CHATBOT: RAG SERVER")

@app.post("/rerank")
async def conversation_endpoint(request: QueryRequest):
    logger.info(Fore.GREEN + "="*50)
    logger.info(Fore.GREEN + "[🔎] Endpoint POST /search reached")
    logger.info(Fore.GREEN + "="*50 + Style.RESET_ALL)

    response = await rerank.rerank(request.points, request.query)
    serialized_response = [point.model_dump() for point in response]

    return JSONResponse(content=serialized_response)

@app.get("/health")
async def health_check():
    logger.info(Fore.GREEN + "="*50)
    logger.info(Fore.GREEN + "[💚] Endpoint GET /health reached")
    logger.info(Fore.GREEN + "="*50 + Style.RESET_ALL)

    response_payload = {
        "staus": 200,
        "message": "🚀 BNB Chatbot API 'rerank_server' are up and running through NGINX load balancer!",
        "data": {
            "service": "bnb-chatbot",
            "version": "1.0.0"
        }
    }

    return JSONResponse(content=response_payload)


def start_server(host: str = "0.0.0.0", port: int = 8002):
    # Uvicorn
    uvicorn.run(
        "app.endpoint:app", 
        host=host, 
        port=port, 
        reload=False,
        log_level="info",
        log_config="config/logconfig.json",
        workers=1
    )
