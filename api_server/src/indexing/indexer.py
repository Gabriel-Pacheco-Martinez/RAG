# General
from colorama import Fore, Style

# Numpy
import numpy as np

# Qdrant
from qdrant_client.models import Distance, VectorParams, SparseVectorParams, PointStruct, Modifier, Document
from qdrant_client import AsyncQdrantClient

# Logging
import logging
logger = logging.getLogger(__name__)

class Indexer():
    def __init__(self, client:AsyncQdrantClient, dim:int):
        self.client = client
        self.dim = dim

    async def _create_collection(self, name: str):
        # Delete if it exists
        try:
            await self.client.delete_collection(name)
        except Exception:
            pass  # collection did not exist

        # Recreate
        await self.client.create_collection(
            collection_name=name,
            vectors_config={    
                "dense": VectorParams(
                    distance=Distance.COSINE,
                    size=self.dim
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(
                    modifier=Modifier.IDF
                )
            }
        )

    async def _setup_collections(self):
        await self._create_collection("documentos")
        await self._create_collection("capitulos")
        await self._create_collection("textos")

    async def _index_texto(self, doc_id:str, cap_id:str, texto_id: str, embedding: np.ndarray, texto: str, doc_titulo: str, cap_titulo: str, doc_texto: str, cap_texto: str):
        await self.client.upsert(
            collection_name="textos",
            points=[
                PointStruct(
                    id=int(texto_id),
                    vector={
                        "dense": embedding.tolist(), # Qdrant requires list, not np.array
                        "sparse": Document(
                            text=texto,
                            model="Qdrant/bm25"
                        )
                    },
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

    async def _index_capitulo(self, doc_id:str, cap_id:str, embedding: np.ndarray, texto: str, cap_metadata: dict):
        await self.client.upsert(
            collection_name="capitulos",
            points=[
                PointStruct(
                    id=int(cap_id),
                    vector={
                        "dense": embedding.tolist(), # Qdrant requires list, not np.array
                        "sparse": Document(
                            text=texto,
                            model="Qdrant/bm25"
                        )
                    },
                    payload={
                        "cap_id": cap_id,
                        "doc_id": doc_id,
                        "titulo": cap_metadata["titulo"], 
                        "texto": texto
                    }
                )
            ]
        )

    async def _index_documento(self, doc_id:str, embedding: np.ndarray, texto: str, doc_metadata: dict):
        await self.client.upsert(
            collection_name="documentos",
            points=[
                PointStruct(
                    id=int(doc_id),
                    vector={
                        "dense": embedding.tolist(), # Qdrant requires list, not np.array
                        "sparse": Document(
                            text=texto,
                            model="Qdrant/bm25"
                        )
                    },
                    payload={
                        "doc_id": doc_id,
                        "titulo": doc_metadata["titulo"], 
                        "texto": texto
                    }
                )
            ]
        )

    async def index_embeddings(self, metadata: dict, embeddings: dict):
        await self._setup_collections()

        # Index documentos
        for doc_id, doc_metadata in metadata["documentos"].items():
            embedding = embeddings["documentos"][doc_id]["embedding"]
            doc_texto = embeddings["documentos"][doc_id]["text"]
            doc_titulo = doc_metadata["titulo"]
            await self._index_documento(doc_id, embedding, doc_texto, doc_metadata)

            # Index capitulos dentro de documentos
            for cap_id in doc_metadata["capitulos_ids"]:
                embedding = embeddings["capitulos"][cap_id]["embedding"]
                cap_texto = embeddings["capitulos"][cap_id]["text"]
                cap_metadata = metadata["capitulos"][cap_id]
                cap_titulo = cap_metadata["titulo"]
                await self._index_capitulo(doc_id, cap_id, embedding, cap_texto, cap_metadata)

                # Index textos dentro de capitulos
                for texto_id in cap_metadata["textos_ids"]:
                    embedding = embeddings["textos"][texto_id]["embedding"]
                    texto = embeddings["textos"][texto_id]["text"]
                    await self._index_texto(doc_id, cap_id, texto_id, embedding, texto, doc_titulo, cap_titulo, doc_texto, cap_texto)
