import torch
import torch.nn.functional as F
import numpy as np

from transformers import AutoModel, AutoTokenizer

def _mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

class ChunkEmbedder:
    def __init__(self, model_name: str, batch_size: int):
        self.model_name = model_name
        self.batch_size = batch_size

    def load_model(self):
        try:
            # Use HF to load model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(f'sentence-transformers/{self.model_name}')
            self.model = AutoModel.from_pretrained(f'sentence-transformers/{self.model_name}')
            self.model.eval()  # Set the model to evaluation mode
            # print(f"Successfully loaded model and tokenizer for: {self.model_name}")
        except Exception as e:
            raise Exception(f"Error loading embedding model and tokenizer: {self.model_name}: {e}")

    def embed_chunks(self, chunks) -> list[dict]:
        # Load model
        self.load_model()

        # Prepare inputs
        chunk_ids = []
        chunk_texts = []
        chunk_embeddings = []

        # Break apart the tuple from the JSON
        for chunk_id, chunk in chunks.items(): 
            chunk_ids.append(chunk_id)
            chunk_texts.append(chunk["text"])

        # =======
        # Batch processing 
        """
        Batch processing will be performed to obtain the embeddings because it has
        more efficiency. So all the texts will be tokenized together and passed to the model at once.
        """
        for i in range(0, len(chunk_texts), self.batch_size):
            batch_chunk_ids = chunk_ids[i:i + self.batch_size] # Slicing to get from i to i + batch_size elements
            batch_chunk_texts = chunk_texts[i:i + self.batch_size]

            # Tokenize the batch
            """
            Output for this step is a dictionary with three tensors: Dict[str, torch.Tensor]
            (Batch size = B, Sequence length of tokens per chunk = L).
            Therefore there are B texts with L tokens each. torch.int64 is the datatype to store tokens.
                * input_ids: shape=(B, L), dtype=torch.int64.         => What is the token?
                * attention_mask: shape=(B, L), dtype=torch.int64     => Should the model pay attention to this token?
                * token_type_ids: shape=(B, L), dtype=torch.int64     => Which sentence does this token belong to?
            """
            batch_tokens = self.tokenizer(batch_chunk_texts, padding=True, truncation=True, return_tensors="pt")

            # Compute token embeddings
            """
            Output for this step is an object with two tensors: Dict[str, torch.Tensor]
            (Batch size = B, Sequence length of tokens per chunk = L, Embedding dimension = D).
            Last_hidden_state shops that for each sentence there are 112 tokens, where each token
            is represented by a vector of 384 dimensions. pooler_output doens't capture semantic meaning
                * last_hidden_state: shape=torch.Size([6, 112, 384])(B,L,D)
                * pooler_output: shape=torch.Size([6, 384])(B,D)
            Can be loooked at like:
                - B: each sentence
                - L: each token in the sentence
                - D: vector representing each token
            """
            with torch.no_grad():
                model_output = self.model(**batch_tokens)

            # Mean Pooling: From token level embeddings to sentence level embeddings
            """
            The output is a pyTorch tensor of shape (B, D). Each sentence will be represented
            by a vector of D dimensions. In this case 384 dimensions because of the model.
            """
            embeddings = _mean_pooling(model_output, batch_tokens['attention_mask'])

            # Normalize
            """
            The output is a pyTorch tensor of shape (B, D). Each sentence will be represented
            by a vector of D dimensions. In this case 384 dimensions because of the model.
            """
            embeddings = F.normalize(embeddings, p=2, dim=1)

            # Construct results
            for chunk_id, text, emb in zip(batch_chunk_ids, batch_chunk_texts, embeddings):
                chunk_embeddings.append({
                    "chunk_id": chunk_id,
                    "text": text,
                    "embedding": emb.numpy() # from tensor to np.array
                })

        # Say something
        print(f"\033[92mEmbedded {len(chunk_embeddings)} chunks/sentences, each with {chunk_embeddings[0]['embedding'].shape[0]} dimensions.\033[0m")
        return chunk_embeddings

    def embed_query(self, query: str) -> np.ndarray: 
        # Load model
        self.load_model()

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
        print(f"\033[34mEmbedded number of queries: {embeddings.shape[0]}, each with {embeddings.shape[1]} dimensions\033[0m")
        return embeddings