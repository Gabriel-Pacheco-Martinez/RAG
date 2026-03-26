# Genral
import asyncio

# Qdrant
from qdrant_client.models import ScoredPoint

# Configuration
from config.settings import RERANKER_MODEL

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

async def rerank(points: list[dict], query_text: str) -> list[dict]:
    # # TODO: Check where the model is running
    # # logger.info("The reranker model is running on: %s", RERANKER_MODEL.model.device)
    await asyncio.sleep(0.1)
    return points

    # pairs = []
    # valid_points = []

    # # Create pairs
    # for point in points:
    #     payload = point.get("payload")

    #     if not payload or "texto" not in payload:
    #         logger.warning("[X] Payload does not contain 'texto' key inside reranker")
    #         continue

    #     pairs.append((query_text, payload["texto"]))
    #     valid_points.append(point)

    # # Rerank
    # scores = await asyncio.to_thread(RERANKER_MODEL.predict,pairs,show_progress_bar=False)

    # # Sort 
    # rescored = list(zip(valid_points, scores))
    # rescored.sort(key=lambda x: x[1], reverse=True)
    # top_points: list[dict] = [point for point, _ in rescored[:3]]

    # return top_points