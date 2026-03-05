# General
from time import perf_counter
from colorama import Fore, Style

# LangGraph
from src.models.state import ChatState

# Qdrant
from qdrant_client.models import ScoredPoint

# Helpers
from src.utils.io import read_json
from src.utils.prompts import build_generator_prompt
from src.utils.llm_client import call_llm
from src.utils.llm_client import extract_json_from_response
from src.generation.searcher import search

# Classes
from src.indexing.embedder import Embedder
from langchain_core.prompt_values import PromptValue
from typing import Awaitable

# Configuration
from config.settings import EMBEDDING_MODEL
from config.settings import EMBEDDING_BATCH_SIZE
from config.settings import WEBSITE_METADATA_FILE_PATH

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

def _build_context(vectors: list[ScoredPoint], textos: dict[str, str]) -> str:
        # General information for all chunks
        general_payload = vectors[0].payload
        context = f"""
            DOCUMENTO: {general_payload.get('doc_titulo', '').upper()}
            Resumen del documento: {general_payload.get('doc_resumen', '')}

            CAPÍTULO: {general_payload.get('cap_titulo', '').upper()}
            Descripción del capítulo: {general_payload.get('cap_texto', '')}
        """
        
        # Merge chunk information
        paragraphs = []
        for index, vector in enumerate(vectors):
            payload = vector.payload

            paragraph = f"""
            ---
            CHUNK {index+1}:


            TEXTO: {textos[payload["texto_id"]]}
            """.strip()

            paragraphs.append(paragraph)

        return context + "\n\n".join(paragraphs)


async def llm_generate(state: ChatState) -> ChatState:
    # =======
    # RAG
    # =======
    # Timer
    state["start_timer_llm_rag"] = perf_counter()
    embedder = Embedder(EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE)

    # Query data
    topic = state["topic"]
    query_str = state["user_message"]
    query_embedded = embedder.embed_query(query_str)

    # Search
    vectors: Awaitable[list[ScoredPoint]] = await search(query_embedded, query_str, topic)
    state["document"] = vectors[0].payload.get('doc_titulo', '').upper()
    state["chapter"] = vectors[0].payload.get('cap_titulo', '').upper()
    textos = read_json(WEBSITE_METADATA_FILE_PATH)["textos"]

    # Build context
    context = _build_context(vectors, textos)
    state["context"] = context

    logger.info(Fore.RED + f"{state['user_session_id']}: " +Fore.CYAN + "[✅] 🧰 RAG ACHIEVED: " + Style.RESET_ALL + "it took " + Fore.YELLOW + f"{perf_counter() - state['start_timer_llm_rag']:.4f}s ⏱. ")

    # =======
    # CLIENT
    # =======
    # Timer
    state["start_timer_llm_generate"] = perf_counter()

    # Build prompt and call llm
    generate_prompt: PromptValue = build_generator_prompt(state)
    response: Awaitable[str] = await call_llm(generate_prompt)

    # Update state
    state["llm_query_response"] = f"""
        🤖 Este mensaje esta generado por Inteligencia Artifical. Informacion obtenida de la sección {state["document"]} del capítulo {state["chapter"]}:{response}
        """
    logger.info(Fore.RED + f"{state['user_session_id']}: " + Style.RESET_ALL + f"{state['llm_query_response']}")

    state["conversation_history"].append(f"User:{state['user_message']}")
    state["conversation_history"].append(f"System:{state['llm_query_response']}")

    # Keep only the last 6 messages
    state["conversation_history"] = state["conversation_history"][-6:]

    return state