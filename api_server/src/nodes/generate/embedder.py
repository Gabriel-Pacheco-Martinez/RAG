# General
from colorama import Fore, Style

# Qdrant
from qdrant_client.models import SparseVector

# Torch and numpy
import torch
import torch.nn.functional as F
import numpy as np

# Configuration
from config.settings import SPARSE_MODEL
from config.settings import DENSE_MODEL
from config.settings import DENSE_TOKENIZER

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

def _dense_mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

def get_dense_embedding(query: str) -> np.ndarray:
    # Load model
    DENSE_MODEL.eval()

    # Tokenize the query
    query_tokens = DENSE_TOKENIZER(query, padding=True, truncation=True, return_tensors="pt")

    # Compute token embeddings
    with torch.no_grad():
        model_output = DENSE_MODEL(**query_tokens)

    # Mean Pooling
    embeddings = _dense_mean_pooling(model_output, query_tokens['attention_mask'])

    # Normalize
    embeddings = F.normalize(embeddings, p=2, dim=1)
    embeddings = embeddings.numpy()

    # Say something
    # logger.info(Fore.YELLOW + f"Embedded number of queries: {embeddings.shape[0]}, each with {embeddings.shape[1]} dimensions" + Style.RESET_ALL)

    return embeddings

def get_sparse_embedding(query: str) -> SparseVector:
    sparse_embedding = next(SPARSE_MODEL.embed([query]))
    return SparseVector(
        indices=sparse_embedding.indices.tolist(),
        values=sparse_embedding.values.tolist()
    )