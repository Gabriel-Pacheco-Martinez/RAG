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
from src import search

# Logging
logger = logging.getLogger('uvicorn.error')

@app.post("/search")
async def conversation_endpoint(request: QueryRequest):
    logger.info(Fore.GREEN + "="*50)
    logger.info(Fore.GREEN + "[🤖] Endpoint POST /search reached")
    logger.info(Fore.GREEN + "="*50 + Style.RESET_ALL)

    response = await search.search(request)
    serialized_response = [point.model_dump() for point in response]

    return JSONResponse(content=serialized_response)

def start_server(host: str = "0.0.0.0", port: int = 8002):
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