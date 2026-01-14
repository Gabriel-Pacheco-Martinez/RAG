import re
import uuid
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Tuple

class DocumentChunker(ABC):
    @abstractmethod
    def chunk_document(self, document_text):
        pass
    
class PDFDocumentChunker(DocumentChunker):
    """
    Hierarchical document chunker that organizes content into:
    documents -> chapters -> sections -> chunks
    """
    
    def __init__(self, document_id: int = 1042, author: str = "BNB", date: str =None):
        self.document_id = document_id
        self.author = author
        self.date = date
    
    def chunk_document(self) -> Dict[str, Dict[str, Any]]:
        """Placeholder code just to illustrate structure of output"""
        with open("data/processed/metadata.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # This is dict of chunks. Each chunks is also a dict
        chunks = data["chunks"] 

        # Say something
        print(f"\033[92mCreated {len(chunks)} chunks.\033[0m")
        return chunks


        