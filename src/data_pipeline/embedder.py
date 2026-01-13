import json
import torch
import torch.nn.functional as F

from transformers import AutoModel, AutoTokenizer

def _mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

class ChunkEmbedder:
    def __init__(self, model_name: str, data_path: str, batch_size: int):
        self.model_name = model_name
        self.data_path = data_path
        self.batch_size = batch_size

    def load_model(self):
        # Placeholder for model loading logic
        print(f"Loading embedding model: {self.model_name}")

        # Load the tokenizer and model from Hugging Face
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(f'sentence-transformers/{self.model_name}')
            self.model = AutoModel.from_pretrained(f'sentence-transformers/{self.model_name}')
            self.model.eval()  # Set the model to evaluation mode
            print(f"Successfully loaded model and tokenizer for: {self.model_name}")
        except Exception as e:
            raise Exception(f"Error loading embedding model and tokenizer: {self.model_name}: {e}")

    def embed_chunks(self):
        # Load model
        self.load_model()

        # Load chunk data
        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        chunks = data["chunks"]

        # Prepare inputs
        chunk_ids = []
        chunk_texts = []
        chunk_embeddings = []

        for chunk_id, chunk in chunks.items(): # Break apart the tuple from the JSON
            chunk_ids.append(chunk_id)
            chunk_texts.append(chunk["text"])

        # =======
        # Batch processing 
        """
        Batch processing will be performed to obtain the embeddings because it has
        more efficiency. So all the texts will be tokenized together and passed to the model at once.
        """
        for i in range(0, len(chunk_texts), self.batch_size):
            batch_chunk_ids = chunk_ids[i:i + self.batch_size]
            batch_chunk_texts = chunk_texts[i:i + self.batch_size]

            # Tokenize the batch
            batch_tokens = self.tokenizer(batch_chunk_texts, padding=True, truncation=True, return_tensors="pt")

            # Compute token embeddings
            with torch.no_grad():
                model_output = self.model(**batch_tokens)

            # Mean Pooling
            embeddings = _mean_pooling(model_output, batch_tokens['attention_mask'])

            # Normalize
            embeddings = F.normalize(embeddings, p=2, dim=1)

            # Construct results
            for chunk_id, text, emb in zip(batch_chunk_ids, batch_chunk_texts, embeddings):
                chunk_embeddings.append({
                    "chunk_id": chunk_id,
                    "text": text,
                    "embedding": emb.numpy()
                })

        # Say something
        print(f"\033[92mCreated embeddings for {len(chunk_embeddings)} chunks.\033[0m")
        return chunk_embeddings
