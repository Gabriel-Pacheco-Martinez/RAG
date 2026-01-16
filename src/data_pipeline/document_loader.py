import fitz
import json
from pathlib import Path
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, List

from src.utils.pdf_utils import extract_blocks_from_page


class DocumentLoader(ABC):
    # Abstract base class for document loaders
    def __init__(self, original_docs_folder_path: str, processed_docs_folder_path: str):
        self.original_docs_folder_path = Path(original_docs_folder_path)
        self.processed_docs_folder_path = Path(processed_docs_folder_path)
        if not self.processed_docs_folder_path.exists():
            self.processed_docs_folder_path.mkdir(parents=True, exist_ok=True)
        if not self.original_docs_folder_path.exists():
            raise FileNotFoundError(f"❌ The folder {original_docs_folder_path} does not exist.")

    @abstractmethod
    def load_documents(self):
        pass

class PDFDocumentLoader(DocumentLoader):

    # Concrete implementation for loading PDF documents
    def load_documents(self) -> List[Dict[List,Dict]]:
        documents = []
        doc_count = 0

        for file_object in self.original_docs_folder_path.iterdir():
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
        with open (self.processed_docs_folder_path/"documents.json", "w", encoding="utf-8") as f:
            json.dump(documents, f, ensure_ascii=False, indent=4)

        # Say something
        print(f"\033[92mLoaded {doc_count} documents\033[0m")
        return documents