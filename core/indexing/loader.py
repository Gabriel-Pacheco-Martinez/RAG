# General 
import fitz
from pathlib import Path
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, List
from colorama import Fore, Style

# Helpers
from core.utils.io import read_json
from core.utils.io import write_json
from core.utils.pdf import extract_blocks_from_page

# Logging
import logging
logger = logging.getLogger(__name__)

class DocumentLoader(ABC):
    # Abstract base class for document loaders
    
    @abstractmethod
    def load_documents(self):
        pass

class PDFDocumentLoader(DocumentLoader):
    def __init__(self, PDF_RAW_DOCS_PATH:str, PDF_LOADED_FILE_PATH: str):
        self.pdf_loaded_file_path = PDF_LOADED_FILE_PATH
        self.pdf_raw_docs_path = Path(PDF_RAW_DOCS_PATH) 
        if not self.pdf_raw_docs_path.exists():
            raise FileNotFoundError(f"❌ The folder {PDF_RAW_DOCS_PATH} does not exist.")

    # Concrete implementation for loading PDF documents
    def load_documents(self) -> List[Dict[List,Dict]]:
        documents = []
        doc_count = 0

        for file_object in self.pdf_raw_docs_path.iterdir():
            if not file_object.is_file():
                continue  # Skip non-files
            if not file_object.suffix.lower() == ".pdf":
                continue  # skip non-pdfs

            # Grab current file
            file_str = str(file_object)
            doc = fitz.open(file_str)
            
            # Extract blocks from each file
            doc_lines = []
            doc_fonts = defaultdict(int)
            for page in doc:
                page_lines, page_fonts = extract_blocks_from_page(page, file_object.name)
                doc_lines.extend(page_lines)
                for size, count in page_fonts.items():
                    doc_fonts[size] += count
            
            # Text and fonts for curr document
            doc_count += 1
            doc_info = {
                "lines": doc_lines,
                "fonts": doc_fonts
            }
           
            documents.append(doc_info)

        # Take docs to json to overview
        write_json(documents, self.pdf_loaded_file_path)

        # Say something
        logging.info(Fore.BLUE + f"Loaded {doc_count} documents" + Style.RESET_ALL)
        return documents