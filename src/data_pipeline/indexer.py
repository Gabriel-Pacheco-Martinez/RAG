import faiss
import numpy as np
import json
import os

from abc import ABC, abstractmethod

class VectorIndexer(ABC):

    def __init__(self, dim: int, index_path: str):
        self.dim = dim # Dimension of the vector embeddings
        self.index = faiss.IndexFlatL2(dim)  # Using L2 distance for indexing
        self.metadata = []  # To store metadata associated with each vector
        self.index_path = index_path

    @abstractmethod
    def index_embeddings(self, chunks: list[dict]):
        pass

class FAISSIndexer(VectorIndexer):

    def __init__(self, dim: int, index_path: str):
        super().__init__(dim, index_path)

    def index_embeddings(self, chunks: list[dict]):
        """
        chunks: list of dicts like {'chunk_id': '1', 'text': '...', 'embedding': np.array([...])}
        Index in FAISS and index in list[dict] for metadata match
        """
        # Store metadata
        self.metadata.extend([{'chunk_id': c['chunk_id'], 'text': c['text']} for c in chunks])

        # Extract array of only embeddings
        embeddings = np.array([chunk['embedding'] for chunk in chunks], dtype=np.float32)
        self.index.add(embeddings)

        # Make sure folder exists
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, self.index_path)
        print(f"FAISS index saved to {self.index_path}")
