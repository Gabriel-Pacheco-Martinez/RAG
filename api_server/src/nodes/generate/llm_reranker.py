# General
import ast
import asyncio

# Qdrant
from qdrant_client.models import ScoredPoint

# LangGraph
from src.models.state import ChatState
from langchain_core.prompt_values import PromptValue

# Helpers
from src.utils.prompts import build_reranking_prompt
from src.utils.llm import call_llm

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

async def rerank(state: ChatState, points: list[ScoredPoint], query: str) -> list[dict]:
    await asyncio.sleep(0.5)
    points_serialized: list[dict] = [p.model_dump() if hasattr(p, 'model_dump') else p for p in points]
    return points_serialized

    # Convert from list[ScoredPoint] to list[dict]
    # points_serialized: list[dict] = [p.model_dump() if hasattr(p, 'model_dump') else p for p in points]
    # points_str = "\n\n".join(
    #     f"[{p['id']}] {p['payload']['titulo']}\n{p['payload']['texto']}"
    #     for p in points_serialized
    # )

    # # Build prompt and call llm
    # reranking_prompt: PromptValue = build_reranking_prompt(points_str, query)
    # response: str = await call_llm(state, reranking_prompt)

    # try:
    #     order = ast.literal_eval(response)  # safe parsing
    # except Exception:
    #     logger.warning("Failed to parse LLM rerank output, returning original order")
    #     return points_serialized

    # # Validate output
    # if not isinstance(order, list) or not all(isinstance(i, (str, int)) for i in order):
    #     logger.warning("Invalid rerank format, returning original order")
    #     return points_serialized

    # # Normalize to string IDs
    # order = [str(i) for i in order]
    # valid_ids = {str(p["id"]) for p in points_serialized}

    # # Remove invalid IDs
    # order = [i for i in order if i in valid_ids]

    # # Fill missing IDs (fallback safety)
    # missing = [i for i in valid_ids if i not in order]
    # order.extend(missing)

    # # Map ID → document
    # id_to_doc = {str(p["id"]): p for p in points_serialized}

    # reranked = [id_to_doc[i] for i in order]

    # return reranked

