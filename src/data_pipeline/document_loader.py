import pdfplumber
import os

from unstructured.partition.pdf import partition_pdf
from abc import ABC, abstractmethod

import pymupdf
import pymupdf4llm  # for the markdown conversion
from pathlib import Path

import PyPDF2

class DocumentLoader(ABC):
    # Abstract base class for document loaders
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"The file {file_path} does not exist.")

    @abstractmethod
    def load_document(self):
        pass

class PDFDocumentLoader(DocumentLoader):
    def __init__(self, file_path: str):
        super().__init__(file_path)

    # Concrete implementation for loading PDF documents
    def load_document(self, output_dir: str = None):
        text = ""
        
        try:
            with open(self.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Error loading PDF document: {str(e)}")

    
# class PDFDocumentLoader(DocumentLoader):
#     # Concrete implementation for loading PDF documents
#     def load_document(self, output_dir: str = None):
#         if output_dir:
#             output_dir = Path(output_dir)
#             output_dir.mkdir(parents=True, exist_ok=True)
#         else:
#             output_dir = self.file_path.parent

#         output_path = output_dir / f"{self.file_path.stem}.md"

#         # Open PDF
#         doc = pymupdf.open(self.file_path)

#         # Convert to Markdown
#         md = pymupdf4llm.to_markdown(
#             doc,
#             header=False,
#             footer=False,
#             page_separators=True,
#             ignore_images=True,
#             write_images=False,
#             image_path=None
#         )

#         # Clean encoding
#         md_cleaned = md.encode('utf-8', errors='surrogatepass').decode('utf-8', errors='ignore')

#         # Save to file
#         output_path.write_text(md_cleaned, encoding='utf-8')

#         return output_path