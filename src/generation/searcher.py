# General
from colorama import Fore, Style

# Helpers
from src.utils.printing import pretty_print_hits

# HuggingFace
from sentence_transformers import CrossEncoder

# Numpy 
import numpy as np

# Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Prefetch, Query, QueryRequest, FusionQuery, Fusion, SparseVector, Document

# Sparse embedder
from fastembed import SparseTextEmbedding

# Exceptions
from src.models.exceptions import RetrievalError

# Configuration
from config.settings import TOP_K_DENSE
from config.settings import TOP_K_SPARSE
from config.settings import LIMIT_K_HYBRID

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

class Searcher():
    def __init__(self, client: QdrantClient, threshold: float, RERANKER_MODEL: str):
        self.client = client
        self.sparse_model = SparseTextEmbedding("Qdrant/bm25")
        self.reranker_model = CrossEncoder(RERANKER_MODEL)
        self.threshold = threshold

    def _rerank_vectors(self, hits: object, query_text: str, level: str):
        # Check where the model is running
        logger.info("The reranker model is running on: %s", self.reranker_model.model.device)

        # Prepare query-document pairs
        pairs = [
            (query_text, p.payload["texto"])
            for p in hits.points
        ]

        # Rerank and sort by score
        scores = self.reranker_model.predict(pairs, show_progress_bar=False)
        rescored = list(zip(hits.points, scores))
        rescored.sort(key=lambda x: x[1], reverse=True)

        # Get the top 3 points
        top_points = [point for point, _ in rescored[:3]]
        logger.info(Fore.LIGHTYELLOW_EX + f"Top 3 chunks selected {level}: " + Style.RESET_ALL + f"{top_points}")

        return top_points
    
    def _retreive_best_texto(self, embedded_query: np.ndarray, query_text:str, cap_id: int):
        hits = self.client.query_points(
            collection_name="textos",
            prefetch=[
                # Dense vector search
                Prefetch(
                    query=embedded_query.flatten().tolist(),
                    using="dense", 
                    limit=TOP_K_DENSE
                ),
                # Sparse vector search
                Prefetch(
                    query=Document(
                        text=query_text,
                        model="Qdrant/bm25"
                    ),
                    using="sparse",
                    limit=TOP_K_SPARSE
                )
            ],
            query=FusionQuery(
                fusion=Fusion.RRF,
            ),
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="cap_id",
                        match=MatchValue(value=cap_id)
                    )
                ]
            ),
            limit=LIMIT_K_HYBRID
        )
        # No hits found
        if not hits or not hits.points:
            logger.warning("[X] No relevant 'textos' found")
            raise RetrievalError("No relevant 'textos' found")

        # Rerank
        best_text_vectors =self._rerank_vectors(hits, query_text, "textos")
        return best_text_vectors

    def _retreive_best_capitulo(self, embedded_query: np.ndarray, query_text:str, doc_id: str):
        hits = self.client.query_points(
            collection_name="capitulos",
            prefetch=[
                # Dense vector search
                Prefetch(
                    query=embedded_query.flatten().tolist(),
                    using="dense",
                    limit=TOP_K_DENSE,
                ),
                # Sparse vector search
                Prefetch(
                    query=Document(
                        text=query_text,
                        model="Qdrant/bm25"
                    ),
                    using="sparse",
                    limit=TOP_K_SPARSE
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
            limit=LIMIT_K_HYBRID
        )
        # No hits found
        if not hits or not hits.points:
            logger.warning("[X] No relevant 'capitulos' found")
            raise RetrievalError("No relevant 'capitulos' found")

        # Rerank
        best_cap_ids =self._rerank_vectors(hits, query_text, "capitulos")
        best_cap_id = best_cap_ids[0].payload["cap_id"]
        return best_cap_id

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
        if not hits[0]:
            logger.warning("[X] No relevant 'documento' found")
            raise RetrievalError("No relevant 'documentos' found")
        return hits[0][0].payload["doc_id"]

    def search(self, embedded_query: np.ndarray, query_text: str, topic: str) -> list[dict]:
        # best_doc_id = self.retrieve_best_documento(embedded_query)
        best_doc_id = self._retreive_doc_id_from_topic(topic)
        best_capitulo_id = self._retreive_best_capitulo(embedded_query, query_text, best_doc_id)
        best_texto_vectors = self._retreive_best_texto(embedded_query, query_text, best_capitulo_id)
        return best_texto_vectors
