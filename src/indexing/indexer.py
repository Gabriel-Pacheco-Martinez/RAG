# General
import logging
from colorama import Fore, Style

import faiss
import numpy as np
import json
import os
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class VectorIndexer(ABC):
    def __init__(self, dim: int, index_path: str, metadata_path: str):
        self.dim = dim                      # Vector dimension for embeddings
        self.index_path = index_path        # Path for db
        self.metadata_path = metadata_path  # Path for metadata (in case of FAISS) -> because it can't store metadata
        self.index = faiss.IndexFlatIP(dim) # Using Inner Product for comparison
        self.metadata = []  # List to store metadata of each vector

    @abstractmethod
    def index_embeddings(self, chunks: list[dict]):
        pass

class FAISSIndexer(VectorIndexer):
    def __init__(self, dim: int, index_path: str, metadata_path: str):
        super().__init__(dim, index_path, metadata_path)

    def index_embeddings(self, chunks: list[dict]):
        """
        Index vectors in FAISS and store metadata in JSON for later retrieval.
        The index in the metadata list is the index of the vector in the faiss
        index. They are in parallel so that they can be retrieved together.
        """
        # Ensure folders exist to save data
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)

        # Create metadata list
        self.metadata.extend([{'chunk_id': c['chunk_id'], 'text': c['text']} for c in chunks])

        # Form embeddings as 2D numpy array and store them
        """
        Join the list of embeddings into a 2D numpy array. The first dimension is
        the number of chunks, and the second dimension is the embedding dimension.
            * object.shape => (B,384)
        """
        embeddings = np.array([c['embedding'] for c in chunks], dtype=np.float32)
        self.index.add(embeddings) # index saved to memory
        faiss.write_index(self.index, self.index_path) # index saved to disk

        # Save metadata JSON
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

        # Say something
        logging.info(Fore.BLUE + f"Created {len(chunks)} chunks." + Style.RESET_ALL)