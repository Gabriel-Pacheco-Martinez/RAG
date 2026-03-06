import httpx

class SearchClient:

    def __init__(self, base_url="http://nginx:8080"):
        self.base_url = base_url

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

        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self.base_url}/search", json=payload)

        r.raise_for_status()
        return r.json()