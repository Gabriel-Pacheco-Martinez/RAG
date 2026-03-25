# Genral
import asyncio

# Qdrant
from qdrant_client.models import ScoredPoint

# Configuration
from config.settings import RERANKER_MODEL

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

async def rerank(points: list[ScoredPoint], query_text: str) -> list[ScoredPoint]:
    # TODO: Check where the model is running
    # logger.info("The reranker model is running on: %s", RERANKER_MODEL.model.device)
    # await asyncio.sleep(0.1)
    # return points

    # Document pairs
    pairs = []
    for point in points:
        payload = point.payload
        if not payload or "texto" not in payload:
            logger.warning("[X] Payload does not contain 'texto' key inside reranker")
            # raise RetrievalError("Payload does not contain 'texto' key inside reranker")
        pairs.append((query_text, payload["texto"]))

    # Rerank and sort by scores
    scores = await asyncio.to_thread(RERANKER_MODEL.predict, pairs, show_progress_bar=False)
    rescored = list(zip(points, scores))
    rescored.sort(key=lambda x: x[1], reverse=True)

    # Get the top 3 points
    top_points: list[ScoredPoint] = [point for point, _ in rescored[:3]]

    return top_points