# General
import os
import logging
import json
from colorama import Fore, Style
from abc import ABC, abstractmethod

# Important
import faiss
import numpy as np
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client import QdrantClient


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

class FAISSIndexerHierarchical(VectorIndexer):
    def __init__(self, client:QdrantClient, dim:int):
        self.client = client
        self.dim = dim

    def _create_collection(self, name: str):
        try:
            self.client.get_collection(name)
            exists = True
        except Exception:
            exists = False

        if not exists:
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=self.dim,
                    distance=Distance.COSINE
                )
            )
        
    def _setup_collections(self):
        self._create_collection("documentos")
        self._create_collection("capitulos")
        self._create_collection("textos")

    def _index_texto(self, doc_id:str, cap_id:str, texto_id: str, embedding: np.ndarray, texto: str):
        self.client.upsert(
            collection_name="textos",
            points=[
                PointStruct(
                    id=int(texto_id),
                    vector=embedding.tolist(), # Qdrant requires list, not np.array
                    payload={
                        "texto_id": texto_id,
                        "cap_id": cap_id,
                        "doc_id": doc_id,
                        "texto": texto
                    }
                )
            ]
        )

    def _index_capitulo(self, doc_id:str, cap_id:str, embedding: np.ndarray, texto: str, cap_metadata: dict):
        self.client.upsert(
            collection_name="capitulos",
            points=[
                PointStruct(
                    id=int(cap_id),
                    vector=embedding.tolist(), # Qdrant requires list, not np.array
                    payload={
                        "cap_id": cap_id,
                        "doc_id": doc_id,
                        "titulo": cap_metadata["titulo"], 
                        "texto": texto
                    }
                )
            ]
        )

    def _index_documento(self, doc_id:str, embedding: np.ndarray, texto: str, doc_metadata: dict):
        self.client.upsert(
            collection_name="documentos",
            points=[
                PointStruct(
                    id=int(doc_id),
                    vector=embedding.tolist(), # Qdrant requires list, not np.array
                    payload={
                        "doc_id": doc_id,
                        "titulo": doc_metadata["titulo"], 
                        "texto": texto
                    }
                )
            ]
        )

    def index_embeddings(self, metadata: dict, embeddings: dict):
        self._setup_collections()

        # Index documentos
        for doc_id, doc_metadata in metadata["documentos"].items():
            embedding = embeddings["documentos"][doc_id]["embedding"]
            texto = embeddings["documentos"][doc_id]["text"]
            self._index_documento(doc_id, embedding, texto, doc_metadata)

            # Index capitulos dentro de documentos
            for cap_id in doc_metadata["capitulos_ids"]:
                embedding = embeddings["capitulos"][cap_id]["embedding"]
                texto = embeddings["capitulos"][cap_id]["text"]
                cap_metadata = metadata["capitulos"][cap_id]
                self._index_capitulo(doc_id, cap_id, embedding, texto, cap_metadata)

                # Index textos dentro de capitulos
                for texto_id in cap_metadata["textos_ids"]:
                    embedding = embeddings["textos"][texto_id]["embedding"]
                    texto = embeddings["textos"][texto_id]["text"]
                    self._index_texto(doc_id, cap_id, texto_id, embedding, texto)
