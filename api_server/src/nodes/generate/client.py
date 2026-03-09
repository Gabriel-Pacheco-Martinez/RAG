# General
from time import perf_counter
from colorama import Fore, Style

# LangGraph
from src.models.state import ChatState

# Qdrant
from qdrant_client.models import ScoredPoint
from qdrant_client.models import SparseVector

# Helpers
from src.nodes.generate.embedder import get_dense_embedding
from src.nodes.generate.embedder import get_sparse_embedding
from src.utils.io import read_json
from src.utils.prompts import build_generator_prompt
from src.utils.llm import call_llm

# Classes
from langchain_core.prompt_values import PromptValue
from src.nodes.generate.api import SearchClient

# Configuration
from config.settings import EMBEDDING_BATCH_SIZE
from config.settings import WEBSITE_METADATA_FILE_PATH
from config.settings import RAG_SERVER_URL

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

def _build_context(vectors: list[dict], textos: dict[str, str]) -> str:
        # General information for all chunks
        general_payload = vectors[0]["payload"]
        if general_payload is None:
            logger.warning("[X] General information is empty while building context")
            raise Exception("General information is empty while building context")

        context = f"""
            DOCUMENTO: {general_payload.get('doc_titulo', '').upper()}
            Resumen del documento: {general_payload.get('doc_resumen', '')}

            CAPÍTULO: {general_payload.get('cap_titulo', '').upper()}
            Descripción del capítulo: {general_payload.get('cap_texto', '')}
        """
        
        # Merge chunk information
        paragraphs = []
        for index, vector in enumerate(vectors):
            payload = vector["payload"]
            if payload is None:
                logger.warning("[X] Vector information is empty while building context")
                raise Exception("Vector information is empty while building context")
            paragraph = f"""
            ---
            CHUNK {index+1}:

            TEXTO: {textos[payload["texto_id"]]}
            """.strip()
            paragraphs.append(paragraph)

        return context + "\n\n".join(paragraphs)


async def llm_generate(state: ChatState) -> ChatState:
    # =======
    # EMBEDDING
    # =======
    # Timer
    state["start_timer_embedding"] = perf_counter()

    # Embeddings
    query = state.get("user_message_str")
    if not query:
        raise Exception("User message is empty before embedding")
    dense_embedding = get_dense_embedding(query)
    sparse_embedding: SparseVector = get_sparse_embedding(query)

    logger.info(Fore.CYAN + "[✅] 🧰 Embedding time: " + Style.RESET_ALL + "it took " + Fore.YELLOW + f"{perf_counter() - state['start_timer_embedding']:.4f}s ⏱. ")

    # =======
    # RAG
    # =======
    # Timer
    state["start_timer_llm_rag"] = perf_counter()

    # Query data
    topic = state.get("topic_llm")
    if not topic:
        raise Exception("Topic is empty before RAG")
    client = SearchClient(RAG_SERVER_URL)
    vectors: list[dict] = await client.search(query, dense_embedding, sparse_embedding, topic)
    textos = read_json(WEBSITE_METADATA_FILE_PATH)["textos"]

    # Document and chapter
    payload_main_vector = vectors[0]["payload"]
    if payload_main_vector is None:
        logger.warning("[X] Payload is empty before RAG")
        raise Exception("Payload is empty before RAG")

    state["document"] = payload_main_vector.get('doc_titulo', '').upper()
    state["chapter"] = payload_main_vector.get('cap_titulo', '').upper()

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
    response: str = await call_llm(generate_prompt)

    # Update state
    state["generate_llm"] = f"""
        🤖 Este mensaje esta generado por Inteligencia Artifical. Informacion obtenida de la sección {state["document"]} del capítulo {state["chapter"]}:{response}
        """
    # Ensure conversation_history exists and is a list
    conversation_history = state.get("conversation_history")
    if conversation_history is None:
        conversation_history = []
        state["conversation_history"] = conversation_history

    # Append messages
    conversation_history.append(f"User:{state.get('user_message_str')}")
    conversation_history.append(f"System:{state['generate_llm']}")

    # Keep only the last 6 messages
    state["conversation_history"] = conversation_history[-6:]

    # Timer
    logger.info(Fore.RED + f"{state['user_session_id']}: " + Style.RESET_ALL + f"{state['generate_llm']}")
    logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + "[✅] 👾 QUERY ANSWERED: " + Style.RESET_ALL + "it took " + Fore.YELLOW + f"{perf_counter() - state['start_timer_llm_generate']:.4f}s ⏱. ")

    return state