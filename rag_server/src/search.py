# General
import asyncio
from colorama import Fore, Style

# Numpy 
import numpy as np

# Qdrant
from qdrant_client.models import Filter
from qdrant_client.models import FieldCondition
from qdrant_client.models import MatchValue
from qdrant_client.models import Prefetch
from qdrant_client.models import FusionQuery
from qdrant_client.models import Fusion
from qdrant_client.models import Document
from qdrant_client.models import SparseVector
from qdrant_client.models import ScoredPoint
from qdrant_client.http.models import QueryResponse

# Models
from src.models.query import QueryRequest

# Exceptions
from src.models.exceptions import RetrievalError

# Configuration
from config.settings import TOP_K_DENSE
from config.settings import TOP_K_SPARSE
from config.settings import LIMIT_K_HYBRID
from config.settings import RERANKER_MODEL
from config.settings import ASYNC_QDRANT_CLIENT

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

async def _rerank_vectors(hits: QueryResponse, query_text: str, level: str) -> list[ScoredPoint]:
    # TODO: Check where the model is running
    # logger.info("The reranker model is running on: %s", RERANKER_MODEL.model.device)

    # Document pairs
    pairs = []
    for point in hits.points:
        payload = point.payload
        if not payload or "texto" not in payload:
            logger.warning("[X] Payload does not contain 'texto' key inside reranker")
            raise RetrievalError("Payload does not contain 'texto' key inside reranker")
        pairs.append((query_text, payload["texto"]))

    # Rerank and sort by score
    scores = await asyncio.to_thread(RERANKER_MODEL.predict, pairs, show_progress_bar=False)
    rescored = list(zip(hits.points, scores))
    rescored.sort(key=lambda x: x[1], reverse=True)

    # Get the top 3 points
    top_points: list[ScoredPoint] = [point for point, _ in rescored[:3]]

    return top_points

async def _retreive_best_texto(query: str, dense_embedding: list, sparse_vector: SparseVector, cap_id: str) -> list[ScoredPoint]:

    hits: QueryResponse = await ASYNC_QDRANT_CLIENT.query_points(
        collection_name="textos",
        prefetch=[
            # Dense vector search
            Prefetch(
                query=dense_embedding,
                using="dense", 
                limit=TOP_K_DENSE
            ),
            # Sparse vector search
            Prefetch(
                query=sparse_vector,
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
    if not hits.points:
        logger.warning("[X] No relevant 'textos' found")
        raise RetrievalError("No relevant 'textos' found")

    # Rerank
    best_text_vectors: list[ScoredPoint] = await _rerank_vectors(hits, query, "textos")
    if not best_text_vectors:
        logger.warning("[X] No relevant 'textos' found after reranking")
        raise RetrievalError("No relevant 'textos' found after reranking")
    
    return best_text_vectors

async def _retreive_best_capitulo(query: str, dense_embedding: list, sparse_vector: SparseVector, doc_id: str) -> str:

    hits: QueryResponse = await ASYNC_QDRANT_CLIENT.query_points(
        collection_name="capitulos",
        prefetch=[
            # Dense vector search
            Prefetch(
                query=dense_embedding,
                using="dense",
                limit=TOP_K_DENSE,
            ),
            # Sparse vector search
            Prefetch(
                query=sparse_vector,
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
    if not hits.points:
        logger.warning("[X] No relevant 'capitulos' found")
        raise RetrievalError("No relevant 'capitulos' found")

    # Rerank
    best_cap_vectors: list[ScoredPoint] = await _rerank_vectors(hits, query, "capitulos")
    if not best_cap_vectors[0]:
        logger.warning("[X] No most relevant 'capitulos' found")
        raise RetrievalError("No most relevant 'capitulos' found")
    
    best_cap_payload = best_cap_vectors[0].payload
    if best_cap_payload is None or "cap_id" not in best_cap_payload:
        logger.warning("[X] Capitulo payload does not contain 'cap_id' key")
        raise RetrievalError("Capitulo payload does not contain 'cap_id' key")

    best_cap_id = best_cap_payload["cap_id"]
    return best_cap_id

async def _retreive_doc_id_from_topic(topic: str) -> str:
    hits = await ASYNC_QDRANT_CLIENT.scroll(
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
    documents, _ = hits
    if not documents:
        logger.warning("[X] No relevant 'documento' found. Topic not in documents.")
        raise RetrievalError("No relevant 'documentos' found. Topic not in documents.")
    
    payload = hits[0][0].payload
    if payload is None or "doc_id" not in payload:
        logger.warning("[X] Document payload does not contain 'doc_id' key")
        raise RetrievalError("Document payload does not contain 'doc_id' key")

    doc_id: str = payload["doc_id"]
    return doc_id

async def search(request: QueryRequest) -> list[ScoredPoint]:
    sparse_vector: SparseVector = SparseVector(
        indices=request.sparse_embedding.indices,
        values=request.sparse_embedding.values
    )
    best_doc_id: str = await _retreive_doc_id_from_topic(request.topic)
    best_capitulo_id: str = await _retreive_best_capitulo(request.query, request.dense_embedding, sparse_vector, best_doc_id)
    best_texto_vectors: list[ScoredPoint] = await _retreive_best_texto(request.query, request.dense_embedding, sparse_vector, best_capitulo_id)
    return best_texto_vectors

    
