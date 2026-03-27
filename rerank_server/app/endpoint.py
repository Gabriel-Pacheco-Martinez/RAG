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

# Configuration
from config.settings import RERANKER_MODEL

# Classes
from src import rerank

# Logging
logger = logging.getLogger('uvicorn.error')

app = FastAPI(title="BNB CHATBOT: RAG SERVER")

@app.get("/health")
async def health_check():
    logger.info(Fore.GREEN + "[💚] Endpoint GET /health reached" + Style.RESET_ALL)

    response_payload = {
        "staus": 200,
        "message": "🚀 BNB Chatbot API 'rerank_server' is up and running through NGINX load balancer!",
        "data": {
            "service": "bnb-chatbot",
            "version": "1.0.0"
        }
    }

    return JSONResponse(content=response_payload)

@app.post("/rerank")
async def conversation_endpoint(request: QueryRequest):
    logger.info(Fore.GREEN + "[🔎] Endpoint POST /search reached" + Style.RESET_ALL)
    response: list[dict] = await rerank.rerank(request.points, request.query)
    return JSONResponse(content=response)

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
