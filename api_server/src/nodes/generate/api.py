# General
import httpx

# Qdrant
from qdrant_client.models import ScoredPoint

# Exceptions
from src.models.exceptions import RerankError

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

class RerankClient:

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(120.0, connect=10.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )

    async def rerank(self, points: list[ScoredPoint], query: str):

        # Convert from list[ScoredPoint] to list[dict]
        points_serialized: list[dict] = [p.model_dump() if hasattr(p, 'model_dump') else p for p in points]

        payload = {
            "points": points_serialized,
            "query": query
        }

        # Post to nginx to contact a rerank server
        try:
            r = await self.client.post(f"{self.base_url}/rerank", json=payload)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"[X] Error inside the reranker.")
            raise RerankError(f" Error inside the reranker.")