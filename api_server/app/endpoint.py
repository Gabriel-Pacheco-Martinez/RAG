"""
Author: Gabriel Pacheco
Date: February 2026
"""
# General
from colorama import Fore, Style
import logging
import secrets

# Server
import uvicorn 

# Helpers
from src.nodes.generate.searcher import search # FIXME: This is only for testing recall and precision, should be removed in production
from src.utils.usage import usage_tracker

# Models
from src.models.query import QueryRequest, SearchPayload

# FastAPI
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Depends, Security, HTTPException, status
from fastapi.security import APIKeyHeader
from fastapi import UploadFile, Form, File
from fastapi import APIRouter

# Classes
from src import graph
from src import index

# Configuration
from config.settings import settings


# Logging
logger = logging.getLogger('uvicorn.error')

# ============================================================
# API KEY Security
# ============================================================
API_KEY = settings.PROTECTION_KEY
API_KEY_HEADER = APIKeyHeader(name="Chatbot-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if not api_key or not secrets.compare_digest(api_key, API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Invalid or missing API key"
        )
    return api_key

# ============================================================
# Routes: Define app and routers
# ============================================================
app = FastAPI(title="BNB CHATBOT")
public_router = APIRouter() # No api key required
protected_router = APIRouter(dependencies=[Depends(verify_api_key)])

# ============================================================
# Endpoint: Process that works with audio also
# ============================================================
# @app.post("/audio")
# async def audio_endpoint(TextChatbot: str = Form(None), AudioChatbot: UploadFile = File(None)):
#     logger.info(Fore.GREEN + "="*50)
#     logger.info(Fore.GREEN + "[🤖] Endpoint POST /audio reached")
#     logger.info(Fore.GREEN + "="*50 + Style.RESET_ALL)

#     if AudioChatbot is not None:
#         audio_bytes = await AudioChatbot.read()
#         request = QueryRequest(session_id=10, mensaje=audio_bytes)
#     if TextChatbot is not None:
#         request = QueryRequest(session_id=10, mensaje=TextChatbot)

#     response = graph.run(request)

#     return JSONResponse(content=response)

# ============================================================
# Endpoint: To test recall and precision
# ============================================================
# @app.post("/search")
# async def searching(payload: SearchPayload):
#     results = await search(**payload.model_dump()) 
#     dict_results = [result.model_dump() for result in results]
#     return JSONResponse(content=dict_results)

# ============================================================
# Public Endpoint: Check health status
# ============================================================
@public_router.get("/api/health")
async def health_check():
    logger.info(Fore.GREEN + "[💚] Endpoint GET /health reached" + Style.RESET_ALL)

    response_payload = {
        "staus": 200,
        "message": "🚀 BNB Chatbot API 'api_server' is up and running!",
        "data": {
            "service": "bnb-chatbot",
            "version": "1.0.0"
        }
    }

    return JSONResponse(content=response_payload)

# ============================================================
# Protected Endpoint: Index documents into Qdrant DB
# ============================================================
@protected_router.get("/index")
async def index_endpoint():
    logger.info(Fore.GREEN + "[📚] Endpoint GET /index reached" + Style.RESET_ALL)

    response = await index.run()

    response_payload = {
        "status": 200,
        "message": response,
        "data": {}
    }

    return JSONResponse(content=response_payload)

# ============================================================
# Protected Endpoint: Respond a text query
# ============================================================
@protected_router.post("/conversation")
async def conversation_endpoint(request: QueryRequest):
    logger.info(Fore.GREEN + "="*50)
    logger.info(Fore.GREEN + "[🤖] Endpoint POST /conversation reached")
    logger.info(Fore.GREEN + "="*50 + Style.RESET_ALL)

    # Get response
    response, usage = await graph.run(request)

    # Total cost and tokens forever
    await usage_tracker.add(**usage)
    logger.info(Fore.YELLOW + f"📊 Total cost so far: ${usage_tracker.total_cost:.6f} for {usage_tracker.total_input_tokens} input tokens and {usage_tracker.total_output_tokens} output tokens" + Style.RESET_ALL)

    return JSONResponse(content=response)

# ============================================================
# START SERVER: Add routes to routers and start Uvicorn server
# ============================================================
app.include_router(public_router)
app.include_router(protected_router)
def start_server(host: str = "0.0.0.0", port: int = 8000):
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