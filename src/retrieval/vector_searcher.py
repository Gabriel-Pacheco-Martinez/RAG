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
            # print(f"Loaded metadata with {len(self.metadata)} chunks")
        else:
            self.metadata = []
            print("Warning: metadata file not found!")

    def search(self, query_embedding: np.ndarray, threshold: float = 0.5, top_k: int = 5) -> list[dict]:
        """
        query_embedding: np.ndarray of shape(1, dim)
        top_k: number of nearest neighbors to retrieve
        """
        # Convert embeddings to float32 as required by faiss
        query_embedding = query_embedding.astype(np.float32)

        # Perform search
        """
        Both are 2D arrays
        distances: shape (1, top_k) -> distances to nearest neighbors
        indices: shape (1, top_k)   -> indices of nearest neighbors
        """
        distances, indices = self.index.search(query_embedding, top_k)

        # Select nearest vector neighbours
        neighbour_vectors = []

        for sim, idx in zip(distances[0], indices[0]):
            # Check if similar enough and if index exists in metadata list
            if sim > threshold and idx < len(self.metadata): 
                neighbour_vectors.append({
                    "chunk_id": self.metadata[idx]['chunk_id'],
                    "text": self.metadata[idx]['text'],
                    "similarity": float(sim)
                })

        # Say something
        print(f"\033[34mRetrieved {len(neighbour_vectors)} vectors.\033[0m")
        return neighbour_vectors