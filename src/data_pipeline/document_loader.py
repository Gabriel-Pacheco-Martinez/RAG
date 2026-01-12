import pdfplumber
import os
from abc import ABC, abstractmethod

class DocumentLoader(ABC):
    # Abstract base class for document loaders

    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        self.file_path = file_path

    @abstractmethod
    def load_document(self):
        pass

class PDFDocumentLoader(DocumentLoader):
    # Concrete implementation for loading PDF documents

    def load_document(self):
        with pdfplumber.open(self.file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text