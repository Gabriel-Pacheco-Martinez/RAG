# General
from colorama import Fore, Style
from typing import Dict, Any
from time import perf_counter

# Torch and numpy
import torch
import torch.nn.functional as F
import numpy as np

# Huggingface
from transformers import AutoModel, AutoTokenizer

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

def _mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

class Embedder:
    def __init__(self, model_name: str, batch_size: int):
        self.model_name = model_name
        self.batch_size = batch_size
    
    def _load_model(self):
        try:
            # Use HF to load model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(f'sentence-transformers/{self.model_name}')
            self.model = AutoModel.from_pretrained(f'sentence-transformers/{self.model_name}')
            self.model.eval()  # Set the model to evaluation mode
        except Exception as e:
            raise Exception(f"Error loading embedding model and tokenizer: {self.model_name}: {e}")
        
    def embed_chunks(self, chunks: dict) -> dict:
        # Load model
        self._load_model()
        chunk_embeddings = {
            "documentos": {},
            "capitulos": {},
            "textos": {}
        }

        for chunk_type, chunk_data in chunks.items():
            # Prepare inputs
            chunk_ids = []
            chunk_texts = []

            # Break apart the chunk tuple
            for id, text in chunk_data.items(): 
                chunk_ids.append(id)
                chunk_texts.append(text)

            # Batch processing
            for i in range(0, len(chunk_texts), self.batch_size):
                batch_chunk_ids = chunk_ids[i:i + self.batch_size] # Slicing to get from i to i + batch_size elements
                batch_chunk_texts = chunk_texts[i:i + self.batch_size]

                # Tokenize the batch
                batch_tokens = self.tokenizer(batch_chunk_texts, padding=True, truncation=True, return_tensors="pt")

                # Compute token embeddings
                with torch.no_grad():
                    model_output = self.model(**batch_tokens)

                # Mean Pooling: From token level embeddings to sentence level embeddings
                embeddings = _mean_pooling(model_output, batch_tokens['attention_mask'])

                # Normalize
                embeddings = F.normalize(embeddings, p=2, dim=1)

                # Construct results
                for chunk_id, text, emb in zip(batch_chunk_ids, batch_chunk_texts, embeddings):
                    chunk_embeddings[chunk_type][chunk_id] = {
                        "chunk_id": chunk_id,
                        "text": text,
                        "embedding": emb.numpy() # from tensor to np.array
                    }

        return chunk_embeddings
    
    def embed_query(self, query: str) -> np.ndarray: 
        # Timer
        time = perf_counter()

        # Load model
        self._load_model()

        # Tokenize the query
        query_tokens = self.tokenizer(query, padding=True, truncation=True, return_tensors="pt")

        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**query_tokens)

        # Mean Pooling
        embeddings = _mean_pooling(model_output, query_tokens['attention_mask'])

        # Normalize
        embeddings = F.normalize(embeddings, p=2, dim=1)
        embeddings = embeddings.numpy()

        # Say something
        logger.info(Fore.YELLOW + f"Embedded number of queries: {embeddings.shape[0]}, each with {embeddings.shape[1]} dimensions" + Style.RESET_ALL)
        logger.info(Fore.CYAN + "[✅] 🧰 Embedding time: " + Style.RESET_ALL + "it took " + Fore.YELLOW + f"{perf_counter() - time:.4f}s ⏱. ")

        return embeddings
