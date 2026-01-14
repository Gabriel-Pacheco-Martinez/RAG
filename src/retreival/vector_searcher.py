import faiss
import numpy as np
import json
import os
from abc import ABC, abstractmethod

class VectorSearcher(ABC):
    def __init__(self, index_path: str, metadata_path: str):
        self.index_path = index_path
        self.metadata_path = metadata_path

class FAISSSearcher(VectorSearcher):
    def __init__(self, index_path: str, metadata_path: str):
        super().__init__(index_path, metadata_path)
        self.index = faiss.read_index(index_path)

        # Load metadata JSON
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            print(f"Loaded metadata with {len(self.metadata)} chunks")
        else:
            self.metadata = []
            print("Warning: metadata file not found!")

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[dict]:
        """
        query_embedding: np.ndarray of shape (dim,) or (1, dim)
        top_k: number of nearest neighbors to retrieve
        """
        # Ensure query is 2D
        if query_embedding.ndim == 1:
            query_embedding = np.expand_dims(query_embedding, axis=0)

        query_embedding = query_embedding.astype(np.float32)

        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                results.append({
                    "chunk_id": self.metadata[idx]['chunk_id'],
                    "text": self.metadata[idx]['text'],
                    "distance": float(dist)
                })
        return results