import httpx


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

    async def rerank(self, points, query):
        logger.info(points)
        points_serialized = [p.model_dump() if hasattr(p, 'model_dump') else p for p in points]
        logger.info(points_serialized)


        payload = {
            "points": points,
            "query": query
        }

        r = await self.client.post(f"{self.base_url}/rerank", json=payload)
        r.raise_for_status()
        return r.json()