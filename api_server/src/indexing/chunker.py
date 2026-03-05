# General
import re
from colorama import Fore, Style
from abc import ABC, abstractmethod
from typing import Tuple, Any
from itertools import count

# Helpers
from src.utils.io import read_json
from src.utils.io import write_json
from src.utils.pdf import get_fonts

# Logging
import logging
logger = logging.getLogger(__name__)

class WebsiteChunker():
    def __init__(self):
        # ID counters
        self.doc_id = 1
        self.cap_id = 1
        self.text_id = 1
        self.doc_chunk_id = 1
        self.cap_chunk_id = 1
        self.text_chunk_id = 1

        # Maps
        self.documentos = {}
        self.capitulos = {}
        self.textos = {}
        self.chunks = {
            "documentos": {},
            "capitulos": {},
            "textos": {}
        }

    def _process_attributes(self, data: dict, prefix: str) -> list[str]:
        # Attributes ID
        text_id = self.text_id
        self.text_id += 1

        text_chunk_id = self.text_chunk_id
        self.text_chunk_id += 1

        # Construct attributes text metadata
        sections = []
        for key, value in data.items():
            # Skip resumen_capitulo
            if key == "resumen_capitulo":
                continue
            # Skip resumen_rag
            if key == "resumen_rag":
                continue
            # Construct section
            section = (
                f"### SUBTITLE: {key}\n"
                f"### TEXT: {value.strip()}\n"
            )
            sections.append(section)
        text = prefix + "\n\n".join(sections)
        self.textos[str(text_id)] = text
        
        # Provide attributes rag chunk. THIS CAN BE DONE BY AN LLM
        if "resumen_rag" in data:
            chunk = data["resumen_rag"]
            self.chunks["textos"][str(text_chunk_id)] = chunk

        # Return
        return [str(text_chunk_id)]

    def _process_tabs(self, tabs: dict, prefix):
        textos_ids = []
        for tab_key, tab_data in tabs.items():
            texto = f"### TITULO: {tab_key}\n"
            textos_ids.extend(self._process_attributes(tab_data, prefix+texto))

        return textos_ids

    def _process_subcapitulos(self, subcapitulos: dict):
        textos_ids = []
        for subcap_key, subcap_data in subcapitulos.items():
            texto = f"### SUBCAPITULO: {subcap_key}\n"
            # If inside subcapitulo there are tabs
            if "tabs" in subcap_data:
                tabs:dict = subcap_data["tabs"]
                textos_ids.extend(self._process_tabs(tabs, texto))

            # If inside subcapitulo there is simply text
            else:
                textos_ids.extend(self._process_attributes(subcap_data, texto))

        return textos_ids

    def _process_textos(self, cap_data: dict):
        textos_ids = []
        # If inside capitulo there are subcapitulos
        if "subcapitulos" in cap_data:
            subcapitulos:dict = cap_data["subcapitulos"]
            textos_ids.extend(self._process_subcapitulos(subcapitulos))

        # If inside capitulo there are tabs
        elif "tabs" in cap_data:
            tabs:dict = cap_data["tabs"]
            textos_ids.extend(self._process_tabs(tabs, prefix=""))

        # If inside capitulo there is simply text
        else:
            textos_ids.extend(self._process_attributes(cap_data, prefix=""))

        return textos_ids

    def _process_capitulos(self, capitulos: dict):
        cap_ids = []
        for cap_key, cap_data in capitulos.items():
            # Capitulo ID
            cap_id = self.cap_id
            self.cap_id += 1
            cap_chunk_id = self.cap_chunk_id
            self.cap_chunk_id += 1
            cap_ids.append(str(cap_id))

            # Capitulo chunk
            capitulo_chunk = cap_data["resumen_capitulo"]
            self.chunks["capitulos"][str(cap_chunk_id)] = capitulo_chunk

            # Related textos
            textos_ids:list = self._process_textos(cap_data)

            # Update capitulos map
            self.capitulos[str(cap_id)] = {
                "titulo": cap_key,
                "textos_ids": textos_ids
            }

        return cap_ids

    def _process_documentos(self, documentos_personas: dict):
        for doc_key, doc_data in documentos_personas.items():
            # Document IDs
            doc_id = self.doc_id
            self.doc_id += 1
            doc_chunk_id = self.doc_chunk_id
            self.doc_chunk_id += 1

            # Title chunk
            document_chunk = doc_data["resumen_documento"]
            self.chunks["documentos"][str(doc_chunk_id)] = document_chunk

            # Related capitulos
            capitulos = doc_data["capitulos"]
            cap_ids:list = self._process_capitulos(capitulos)
            
            # Update documents map
            self.documentos[str(doc_id)] = {
                "titulo": doc_key,
                "capitulos_ids": cap_ids
            }
            
    def chunk_document(self, WEBSITE_LOADED_FILE_PATH:str) -> dict:
        # Load file
        input_data = read_json(WEBSITE_LOADED_FILE_PATH)

        # Process personas
        if 'personas' in input_data:
            self._process_documentos(input_data['personas'])

        # Process empresas
        if 'empresas' in input_data:
            self._process_documentos(input_data['empresas'])
        
        map = {
            "documentos": self.documentos,
            "capitulos": self.capitulos,
            "textos": self.textos,
            "chunks": self.chunks
        }

        return map

    def save_chunks(self, WEBSITE_METADATA_FILE_PATH:str ,metadata:dict) -> dict[str, dict[str, Any]]:
        write_json(metadata, WEBSITE_METADATA_FILE_PATH)

        chunks = metadata["chunks"]
        logger.info(Fore.YELLOW + f"Created {len(chunks['textos'])} texto chunks." + Style.RESET_ALL)

        return chunks
    
    def get_chunks(self, WEBSITE_METADATA_FILE_PATH:str):
        data = read_json(WEBSITE_METADATA_FILE_PATH)
        chunks = data["chunks"]
        return data, chunks

class PDFChunker():
    def __init__(self):
        self.doc_counter = count(1)
        self.chapter_counter = count(1)
        self.section_counter = count(1)
        self.chunk_counter= count(1)

    def chunk_document(self, documents_info: list[dict]):
        metadata = {
            "documents": {},
            "chapters": {},
            "sections": {},
            "chunks": {}
        }

        chunk_section_id_counter = 0

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

    def save_chunks(self, PDF_METADATA_FILE_PATH:str , metadata: dict) -> dict[str, dict[str, Any]]:
        write_json(metadata, PDF_METADATA_FILE_PATH)

        chunks = metadata["chunks"]
        logger.info(Fore.YELLOW + f"Created {len(chunks['documentos'])} documento chunks." + Style.RESET_ALL)
        logger.info(Fore.YELLOW + f"Created {len(chunks['capitulos'])} capitulo chunks." + Style.RESET_ALL)
        logger.info(Fore.YELLOW + f"Created {len(chunks['textos'])} texto chunks." + Style.RESET_ALL)

        return chunks
    
    def get_chunks(self, PDF_METADATA_FILE_PATH:str):
        pass