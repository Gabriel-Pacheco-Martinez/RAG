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

class Indexer(VectorIndexer):
    def __init__(self, client:QdrantClient, dim:int):
        self.client = client
        self.dim = dim

    def _create_collection(self, name: str):
        # Delete if it exists
        try:
            self.client.delete_collection(name)
        except Exception:
            pass  # collection did not exist

        # Recreate
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

    def _index_texto(self, doc_id:str, cap_id:str, texto_id: str, embedding: np.ndarray, texto: str, doc_titulo: str, cap_titulo: str, doc_texto: str, cap_texto: str):
        self.client.upsert(
            collection_name="textos",
            points=[
                PointStruct(
                    id=int(texto_id),
                    vector=embedding.tolist(), # Qdrant requires list, not np.array
                    payload={
                        "texto_id": texto_id,
                        "texto": texto,
                        "cap_id": cap_id,
                        "cap_titulo": cap_titulo,
                        "cap_texto": cap_texto,
                        "doc_id": doc_id,
                        "doc_titulo": doc_titulo,
                        "doc_resumen": doc_texto
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
            doc_texto = embeddings["documentos"][doc_id]["text"]
            doc_titulo = doc_metadata["titulo"]
            self._index_documento(doc_id, embedding, doc_texto, doc_metadata)

            # Index capitulos dentro de documentos
            for cap_id in doc_metadata["capitulos_ids"]:
                embedding = embeddings["capitulos"][cap_id]["embedding"]
                cap_texto = embeddings["capitulos"][cap_id]["text"]
                cap_metadata = metadata["capitulos"][cap_id]
                cap_titulo = cap_metadata["titulo"]
                self._index_capitulo(doc_id, cap_id, embedding, cap_texto, cap_metadata)

                # Index textos dentro de capitulos
                for texto_id in cap_metadata["textos_ids"]:
                    embedding = embeddings["textos"][texto_id]["embedding"]
                    texto = embeddings["textos"][texto_id]["text"]
                    self._index_texto(doc_id, cap_id, texto_id, embedding, texto, doc_titulo, cap_titulo, doc_texto, cap_texto)

