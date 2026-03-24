import httpx

class SearchClient:

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(120.0, connect=10.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )

    async def search(self, query, dense_embedding, sparse_embedding, topic):

        payload = {
            "query": query,
            "dense_embedding": dense_embedding.flatten().tolist(),
            "sparse_embedding": {
                "indices": sparse_embedding.indices,
                "values": sparse_embedding.values
            },
            "topic": topic
        }

        r = await self.client.post(f"{self.base_url}/search", json=payload)
        r.raise_for_status()
        return r.json()