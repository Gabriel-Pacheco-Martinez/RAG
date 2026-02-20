# General
from colorama import Fore, Style

# Numpy 
import numpy as np

# Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Prefetch, Query, QueryRequest, FusionQuery, Fusion, SparseVector, Document

# Sparse embedder
from fastembed import SparseTextEmbedding

# Logging
import logging
logger = logging.getLogger(__name__)

class Searcher():
    def __init__(self, client: QdrantClient, threshold: float, top_k: int):
        self.client = client
        self.sparse_model = SparseTextEmbedding("Qdrant/bm25")
        self.threshold = threshold
        self.top_k = top_k

    def _to_sparse_vector(self, query_text: str):
        sparse_query_object = next(self.sparse_model.embed(query_text)) # We use next because it returns a generator
        sparse_vector = SparseVector(
            indices=sparse_query_object.indices.tolist(),
            values=sparse_query_object.values.tolist()
        )
        return sparse_vector
    
    def _retreive_best_texto(self, embedded_query: np.ndarray, query_text:str, cap_id: int):
        hits = self.client.query_points(
            collection_name="textos",
            prefetch=[
                # Dense vector search
                Prefetch(
                    query=embedded_query.flatten().tolist(),
                    using="dense", 
                    limit=3
                ),
                # Sparse vector search
                Prefetch(
                    query=Document(
                        text=query_text,
                        model="Qdrant/bm25"
                    ),
                    using="sparse",
                    limit=3
                )
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="cap_id",
                        match=MatchValue(value=cap_id)
                    )
                ]
            ),
            limit=1, # We can change this if we want Reranking
        )
        if hits and hits.points:
            logging.info(hits.points[0].payload["texto_id"])
            return hits.points[0]
        return None

    def _retreive_best_capitulo(self, embedded_query: np.ndarray, query_text:str, doc_id: str):
        if query_text == None:
            print("Query is empty")
            query_text = "Credito Emprendedor Banca Activa."
        hits = self.client.query_points(
            collection_name="capitulos",
            prefetch=[
                # Dense vector search
                Prefetch(
                    query=embedded_query.flatten().tolist(),
                    using="dense",
                    limit=3,
                ),
                # Sparse vector search
                Prefetch(
                    query=Document(
                        text=query_text,
                        model="Qdrant/bm25"
                    ),
                    using="sparse",
                    limit=3
                )
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="doc_id",
                        match=MatchValue(value=doc_id)
                    )
                ]
            ),
            limit=1, # We can change this if we want Reranking.
        )
        if hits and hits.points:
            logging.info(hits.points[0].payload["cap_id"])
            return hits.points[0].payload["cap_id"]
        return 0

    def _retreive_doc_id_from_topic(self, topic: str):
        hits = self.client.scroll(
            collection_name="documentos",
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="titulo",
                        match=MatchValue(value=topic)
                    )
                ]
            ),
            limit=1
        )
        return hits[0][0].payload["doc_id"] if hits[0] else None

    def search(self, embedded_query: np.ndarray, query_text: str, topic: str) -> list[dict]:
        # best_doc_id = self.retrieve_best_documento(embedded_query)
        best_doc_id = self._retreive_doc_id_from_topic(topic)
        best_capitulo_id = self._retreive_best_capitulo(embedded_query, query_text, best_doc_id)
        best_texto_vector = self._retreive_best_texto(embedded_query, query_text, best_capitulo_id)
        return best_capitulo_id
