import re
import uuid
import json
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, List, Any, Tuple
from itertools import count

from src.utils.metadata_utils import get_fonts

class DocumentChunker(ABC):
    def __init__(self, METADATA_PATH: str):
        self.metadata_path = METADATA_PATH
        self.doc_counter = count(1)
        self.chapter_counter = count(1)
        self.section_counter = count(1)
        self.chunk_counter= count(1)

    # In the future this will be a function only for pdfs
    def metadata_generator(self, documents_info: List[Dict]):
        metadata = {
            "documents": {},
            "chapters": {},
            "sections": {},
            "chunks": {}
        }

        # NEW DOCUMENT
        for document_info in documents_info:
            current_doc_id = next(self.doc_counter)
            current_chapter_id = None
            current_section_id = None

            fonts_info = get_fonts(document_info.get("fonts", {}))

            metadata["documents"][current_doc_id] = {
                "title": None,
                "chapters": []
            }

            for line in document_info.get("lines", []):
                font_size = int(line.get("font_size"))
                text = (line.get("text") or "").strip()
                
                # Skip empty lines
                if not text or text in {"•", "-", "–", "—"}:
                    continue

                # ========
                # Document
                if font_size == fonts_info["title"]:
                    metadata["documents"][current_doc_id]["title"] = text

                # ========
                # Chapter
                elif font_size == fonts_info["chapter"]:
                    current_chapter_id = next(self.chapter_counter)
                    current_section_id = None  # reset section

                    metadata["chapters"][current_chapter_id] = {
                        "title": text,
                        "doc_id": current_doc_id,
                        "sections": []
                    }

                    metadata["documents"][current_doc_id]["chapters"].append(current_chapter_id)

                # ========
                # Section
                elif font_size == fonts_info["section"]:
                    current_section_id = next(self.section_counter)
                    chunk_section_id_counter = 0  # reset chunk_section_id

                    metadata["sections"][current_section_id] = {
                        "title": text,
                        "chapter_id": current_chapter_id,
                        "chunks": []
                    }

                    metadata["chapters"][current_chapter_id]["sections"].append(current_section_id)

                # ========
                # Chunk
                elif font_size == fonts_info["chunk"]:
                    if current_section_id is None:
                        continue  # safety guard

                    chunk_id = next(self.chunk_counter)
                    chunk_section_id_counter += 1

                    metadata["chunks"][chunk_id] = {
                        "chunk_id": chunk_id,
                        "chunk_section_id": chunk_section_id_counter,
                        "section_id": current_section_id,
                        "chapter_id": current_chapter_id,
                        "doc_id": current_doc_id,
                        "text": text
                    }

                    metadata["sections"][current_section_id]["chunks"].append(chunk_id)

        return metadata

    def grab_chunks(self, metadata: Dict) -> Dict[str, Dict[str, Any]]:
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

        chunks = metadata["chunks"]

        # Say something
        print(f"\033[92mCreated {len(chunks)} chunks.\033[0m")
        return chunks
    


        