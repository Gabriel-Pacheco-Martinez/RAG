# General
import logging
from xmlrpc import client
from colorama import Fore, Style
import json
import os

# Databases
import faiss
import numpy as np
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)

class Searcher():
    def __init__(self, client: QdrantClient, threshold: float, top_k: int):
        self.client = client
        self.threshold = threshold
        self.top_k = top_k

    def retreive_best_texto(self, embedded_query: np.ndarray, cap_id: int):
        hits = self.client.search(
            collection_name="textos",
            query_vector=embedded_query.flatten().tolist(),
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="cap_id",
                        match=MatchValue(value=cap_id)
                    )
                ]
            ),
            limit=3,
            score_threshold=0.1
        )
        logging.info(hits[0].payload["texto_id"])
        logging.info(hits[0].payload["texto"])
        return hits[0] if hits else None

    def retreive_best_capitulo(self, embedded_query: np.ndarray, doc_id: int):
        hits = self.client.search(
            collection_name="capitulos",
            query_vector=embedded_query.flatten().tolist(),
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="doc_id",
                        match=MatchValue(value=doc_id)
                    )
                ]
            ),
            limit=3,
            score_threshold=0.3
        )
        logging.info(hits[0].payload["cap_id"])
        return hits[0].payload["cap_id"] if hits else None

    def retrieve_best_documento(self, embedded_query: np.ndarray):
        hits = self.client.search(  # Changed from query_points to search
            collection_name="documentos",
            query_vector=embedded_query.flatten().tolist(),  # Changed query
            limit=3,
            score_threshold=0.3  # Threshold muy bajo para general
        )
        logging.info(hits[0].payload["doc_id"])
        return hits[0].payload["doc_id"] if hits else None

    def search(self,embedded_query: np.ndarray) -> list[dict]:
        best_doc_id = self.retrieve_best_documento(embedded_query)
        best_capitulo_id = self.retreive_best_capitulo(embedded_query, best_doc_id)
        texto_most_relevant_vector = self.retreive_best_texto(embedded_query, best_capitulo_id)
        return texto_most_relevant_vector