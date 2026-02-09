# General
import logging
from xmlrpc import client
from colorama import Fore, Style
import json
import os

# Databases
import faiss
import numpy as np
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client import QdrantClient
        # info = self.client.get_collection("documentos")
        # print(info.config.params.vectors)
        # return info

logger = logging.getLogger(__name__)

class FAISSSeacherHierarchical():
    def __init__(self, client: QdrantClient, threshold: float, top_k: int):
        self.client = client
        self.threshold = threshold
        self.top_k = top_k

    def retrieve_best_documento(self, embedded_query: np.ndarray):
        hits = self.client.search(  # Changed from query_points to search
            collection_name="documentos",
            query_vector=embedded_query.flatten().tolist(),  # Changed from query to query_vector
            limit=1,
            score_threshold=self.threshold  # Optional: filter by threshold
        )
        print(hits)
        return hits[0].payload["doc_id"] if hits else None

    def search(self,embedded_query: np.ndarray) -> list[dict]:
        best_doc_id = self.retrieve_best_documento(embedded_query)
        print(f"Best doc id: {best_doc_id}")

class FAISSSearcher():
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
        logging.info(f"Retrieved {len(neighbour_vectors)} vectors.")
        return neighbour_vectors