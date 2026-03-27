# General
from colorama import Fore, Style
from time import perf_counter
import asyncio

# Numpy 
import numpy as np

# Qdrant
from qdrant_client.models import Filter, FieldCondition, MatchValue, Prefetch, FusionQuery, Fusion, SparseVector, ScoredPoint
from qdrant_client.http.models import QueryResponse

# Helpers
from src.nodes.generate.llm_reranker import rerank

# Exceptions
from src.models.exceptions import RetrievalError
from src.models.exceptions import RerankError

# Models
from src.models.query import QueryRequest
from src.nodes.generate.api import RerankClient

# Configuration
from config.settings import settings
from config.settings import ASYNC_QDRANT_CLIENT

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

# Rerank API Client
rerank_client = RerankClient(settings.NGINX_URL)

async def _retreive_best_texto(query: str, dense_embedding: list, sparse_vector: SparseVector, cap_id: str) -> list[ScoredPoint]:
    # Retrieve from Qdrant
    hits: QueryResponse = await ASYNC_QDRANT_CLIENT.query_points(
        collection_name="textos",
        prefetch=[
            # Dense vector search
            Prefetch(
                query=dense_embedding,
                using="dense", 
                limit=settings.TOP_K_DENSE
            ),
            # Sparse vector search
            Prefetch(
                query=sparse_vector,
                using="sparse",
                limit=settings.TOP_K_SPARSE
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
        limit=settings.LIMIT_N_HYBRID_TEXT
    )

    # Validate
    points: list[ScoredPoint] = hits.points 
    if not points:
        logger.warning("[X] No relevant 'textos' found")
        raise RetrievalError("No relevant 'textos' found")
    
    return points

async def _retreive_best_capitulo(state, query: str, dense_embedding: list, sparse_vector: SparseVector, doc_id: str) -> str:
    # Retrieve from Qdrant
    hits: QueryResponse = await ASYNC_QDRANT_CLIENT.query_points(
        collection_name="capitulos",
        prefetch=[
            # Dense vector search
            Prefetch(
                query=dense_embedding,
                using="dense",
                limit=settings.TOP_K_DENSE,
            ),
            # Sparse vector search
            Prefetch(
                query=sparse_vector,
                using="sparse",
                limit=settings.TOP_K_SPARSE
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
        limit=settings.LIMIT_N_HYBRID_CAPS
    )

    # Validate
    points: list[ScoredPoint] = hits.points
    if not points:
        logger.warning("[X] No relevant 'capitulos' found")
        raise RetrievalError("No relevant 'capitulos' found")

    # Rerank
    # reranked_points: list[dict] = await rerank_client.rerank(points, query)
    reranked_points: list[dict] = await rerank(state, points, query)

    # Select
    best_cap_id = reranked_points[0].get("payload",{}).get("cap_id")
    if not best_cap_id:
        logger.warning("[X] No most relevant 'capitulos' found. Reranker failed.")
        raise RerankError("No most relevant 'capitulos' found. Reranker failed.")
    return best_cap_id

async def _retreive_doc_id_from_topic(topic: str) -> str:
    # Retrieve from Qdrant
    points, offset = await ASYNC_QDRANT_CLIENT.scroll(
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

    # Validate
    if not points:
        logger.warning("[X] No relevant 'documento' found. Topic not in documents.")
        raise RetrievalError("No relevant 'documentos' found. Topic not in documents.")
    
    # Select
    best_doc_id = points[0].payload["doc_id"]
    return best_doc_id

async def search(state, query, dense_embedding, sparse_embedding, topic) -> list[ScoredPoint]:
    logger.info(state)
    # Create sparse vector
    sparse_vector = SparseVector(indices=sparse_embedding.indices, values=sparse_embedding.values)
    
    # Hierarchical retrieval
    best_doc_id: str = await _retreive_doc_id_from_topic(topic)
    best_capitulo_id: str = await _retreive_best_capitulo(state, query, dense_embedding, sparse_vector, best_doc_id)
    best_texto_vectors: list[ScoredPoint] = await _retreive_best_texto(query, dense_embedding, sparse_vector, best_capitulo_id)
    return best_texto_vectors



