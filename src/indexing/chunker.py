import logging
from colorama import Fore, Style
from abc import ABC, abstractmethod
from src.utils.io import read_json, write_json
from src.utils.pdf import get_fonts
from typing import Tuple, Any
import re
from itertools import count

logger = logging.getLogger(__name__)

class DocumentChunker(ABC):
    @abstractmethod
    def chunk_document(self):
        pass

    @abstractmethod
    def get_and_save_chunks(self):
        pass

class WebsiteChunkerHierarchical(DocumentChunker):
    def __init__(self):
        # ID counters
        self.doc_id = 1
        self.cap_id = 1
        self.doc_chunk_id = 1
        self.cap_chunk_id = 1
        self.text_chunk_id = 1

        # Maps
        self.documentos = {}
        self.capitulos = {}
        self.chunks = {
            "documentos": {},
            "capitulos": {},
            "textos": {}
        }

    def _process_attributes(self, data: dict, prefix: str) -> str:
        # Attributes ID
        text_id = self.text_chunk_id
        self.text_chunk_id += 1

        # Construct attributes text chunk
        sections = []
        for key, value in data.items():
            # Skip resumen_capitulo
            if key == "resumen_capitulo":
                continue
            # Construct section
            section = (
                f"### SUBTITLE: {key}\n"
                f"### TEXT: {value.strip()}\n"
            )
            sections.append(section)
        text = prefix + "\n\n".join(sections)
        self.chunks["textos"][str(text_id)] = text
        return [str(text_id)]
    
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
            "chunks": self.chunks
        }

        return map

    def get_and_save_chunks(self, WEBSITE_METADATA_FILE_PATH:str ,metadata:dict) -> dict[str, dict[str, Any]]:
        write_json(metadata, WEBSITE_METADATA_FILE_PATH)

        chunks = metadata["chunks"]
        logging.info(Fore.BLUE + f"Created {len(chunks)} chunks." + Style.RESET_ALL)

        return chunks

class WebsiteChunker(DocumentChunker):
    def __init__(self):
        # ID counters
        self.doc_id = 1
        self.cap_id = 1
        self.subcap_id = 1
        self.tab_id = 1
        self.sec_id = 1
        self.subsec_id = 1
        self.chunk_id = 1

        # Maps
        self.documentos = {}
        self.capitulos = {}
        self.subcapitulos = {}
        self.tabs = {}
        self.secciones = {}
        self.subsecciones = {}
        self.chunks = {}

    def parse_subsections_and_chunks(self, text: str) -> list[Tuple[str, list[str]]]:
        # Pattern to match **Title:**
        subsection_pattern = r'\*\*([^*]+):\*\*'
        parts = re.split(subsection_pattern, text)
        
        subsections = []
        
        # If no subsection markers found, treat entire text as chunks without subsection
        if len(parts) == 1:
            chunks = [line.strip() for line in text.split('\n') if line.strip()]
            if chunks:
                return [(None, chunks)]
            return []
        
        # Process parts: parts[0] is before first subsection (usually empty or whitespace)
        # Then alternates: parts[1] = title, parts[2] = content, parts[3] = title, parts[4] = content, ...
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                title = parts[i].strip()
                content = parts[i + 1]
                
                # Split content by newlines to get individual chunks
                chunks = [line.strip() for line in content.split('\n') if line.strip()]
                
                if chunks:  # Only add if there are actual chunks
                    subsections.append((title, chunks))
        
        return subsections

    def _process_top_level(self, data: dict[str, Any]) -> None:
        """Process top-level categories (creditos, ahorro_e_inversion, corporativa)."""
        for doc_key, doc_data in data.items():
            doc_id = self.doc_id
            self.doc_id += 1
            
            cap_ids = []
            
            if 'capitulos' in doc_data:
                for cap_title, cap_content in doc_data['capitulos'].items():
                    cap_id = self._process_capitulo(cap_title, cap_content, doc_id)
                    cap_ids.append(cap_id)
            
            self.documentos[str(doc_id)] = {
                'titulo': doc_key,
                'capitulos': cap_ids
            }
    
    def _process_capitulo(self, title: str, content: dict[str, Any], doc_id: int) -> int:
        """Process a chapter (capitulo)."""
        cap_id = self.cap_id
        self.cap_id += 1
        
        subcap_ids = []
        tab_ids = []
        sec_ids = []
        
        # Check if this chapter has subcapitulos
        if 'subcapitulos' in content:
            for subcap_title, subcap_content in content['subcapitulos'].items():
                subcap_id = self._process_subcapitulo(subcap_title, subcap_content, cap_id, doc_id)
                subcap_ids.append(subcap_id)
        elif 'tabs' in content:
            for tab_title, tab_content in content['tabs'].items():
                tab_id = self._process_tab(
                    tab_title, tab_content,
                    subcap_id=None, cap_id=cap_id, doc_id=doc_id
                )
                tab_ids.append(tab_id)
        else:
            # Process direct sections in this chapter
            for sec_title, sec_content in content.items():
                if sec_title != 'subcapitulos':
                    sec_id = self._process_seccion(sec_title, sec_content, cap_id, doc_id)
                    sec_ids.append(sec_id)
        
        capitulo_data = {
            'titulo': title
        }
        
        if subcap_ids:
            capitulo_data['subcapitulos'] = subcap_ids
        if tab_ids:
            capitulo_data['tabs'] = tab_ids
        if sec_ids:
            capitulo_data['secciones'] = sec_ids
        
        self.capitulos[str(cap_id)] = capitulo_data
        return cap_id
    
    def _process_subcapitulo(self, title: str, content: dict[str, Any], 
                             cap_id: int, doc_id: int) -> int:
        """Process a subcapitulo."""
        subcap_id = self.subcap_id
        self.subcap_id += 1
        
        tab_ids = []
        sec_ids = []
        
        # Check if this subcapitulo has tabs
        if 'tabs' in content:
            for tab_title, tab_content in content['tabs'].items():
                tab_id = self._process_tab(tab_title, tab_content, subcap_id, cap_id, doc_id)
                tab_ids.append(tab_id)
        else:
            # Process direct sections
            for sec_title, sec_content in content.items():
                if sec_title != 'tabs':
                    sec_id = self._process_seccion(sec_title, sec_content, cap_id, doc_id, 
                                                   subcap_id=subcap_id)
                    sec_ids.append(sec_id)
        
        subcapitulo_data = {
            'titulo': title
        }
        
        if tab_ids:
            subcapitulo_data['tabs'] = tab_ids
        if sec_ids:
            subcapitulo_data['secciones'] = sec_ids
        
        self.subcapitulos[str(subcap_id)] = subcapitulo_data
        return subcap_id
    
    def _process_tab(self, title: str, content: dict[str, Any], 
                     subcap_id: int, cap_id: int, doc_id: int) -> int:
        """Process a tab."""
        tab_id = self.tab_id
        self.tab_id += 1
        
        sec_ids = []
        
        for sec_title, sec_content in content.items():
            sec_id = self._process_seccion(sec_title, sec_content, cap_id, doc_id,
                                          subcap_id=subcap_id, tab_id=tab_id)
            sec_ids.append(sec_id)
        
        self.tabs[str(tab_id)] = {
            'titulo': title,
            'secciones': sec_ids
        }
        return tab_id
    
    def _process_seccion(self, title: str, content: str, cap_id: int, doc_id: int,
                         subcap_id: int = None, tab_id: int = None) -> int:
        """
        Process a section (seccion).
        
        The content may contain:
        1. Bold markdown titles (**Title:**) which become subsections
        2. Plain text lines which become chunks
        """
        sec_id = self.sec_id
        self.sec_id += 1
        
        # Parse subsections and chunks from content
        subsections = self.parse_subsections_and_chunks(content)
        
        subsec_ids = []
        chunk_ids = []
        
        if subsections:
            for subsec_title, chunks in subsections:
                if subsec_title:
                    # This is a subsection with title
                    subsec_id = self.subsec_id
                    self.subsec_id += 1
                    
                    # Create chunks for this subsection
                    subsec_chunk_ids = []
                    for chunk_text in chunks:
                        chunk_id = self._create_chunk(
                            chunk_text, sec_id, cap_id, doc_id,
                            subcap_id, tab_id, subsec_id
                        )
                        subsec_chunk_ids.append(chunk_id)
                    
                    # Create subsection
                    self.subsecciones[str(subsec_id)] = {
                        'titulo': subsec_title,
                        'chunks': subsec_chunk_ids
                    }
                    subsec_ids.append(subsec_id)
                else:
                    # No subsection title, create chunks directly under section
                    for chunk_text in chunks:
                        chunk_id = self._create_chunk(
                            chunk_text, sec_id, cap_id, doc_id,
                            subcap_id, tab_id, None
                        )
                        chunk_ids.append(chunk_id)
        
        # Create section
        seccion_data = {
            'titulo': title
        }
        
        if subsec_ids:
            seccion_data['subsecciones'] = subsec_ids
        if chunk_ids:
            seccion_data['chunks'] = chunk_ids
        
        self.secciones[str(sec_id)] = seccion_data
        return sec_id
    
    def _create_chunk(self, text: str, sec_id: int, cap_id: int, doc_id: int,
                     subcap_id: int = None, tab_id: int = None, subsec_id: int = None) -> int:
        """Create a chunk with all relevant parent IDs."""
        chunk_id = self.chunk_id
        self.chunk_id += 1
        
        chunk_data = {
            'chunk_id': chunk_id,
            'text': text,
            'documento_id': doc_id,
            'capitulo_id': cap_id
        }
        
        # Add optional parent IDs if they exist
        if subsec_id:
            chunk_data['subseccion_id'] = subsec_id
        if sec_id:
            chunk_data['seccion_id'] = sec_id
        if tab_id:
            chunk_data['tab_id'] = tab_id
        if subcap_id:
            chunk_data['subcapitulo_id'] = subcap_id
        
        # Reorder to match expected output format
        ordered_chunk = {}
        for key in ['chunk_id', 'subseccion_id', 'seccion_id', 'tab_id', 
                    'subcapitulo_id', 'capitulo_id', 'documento_id', 'text']:
            if key in chunk_data:
                ordered_chunk[key] = chunk_data[key]
        
        self.chunks[str(chunk_id)] = ordered_chunk
        return chunk_id

    def chunk_document(self, WEBSITE_LOADED_FILE_PATH:str) -> dict:
        # Load file
        input_data = read_json(WEBSITE_LOADED_FILE_PATH)
        
        # Process personas
        if 'personas' in input_data:
            self._process_top_level(input_data['personas'])

        # Process empresas
        if 'empresas' in input_data:
            self._process_top_level(input_data['empresas'])
        
        return {
            'documentos': self.documentos,
            'capitulos': self.capitulos,
            'subcapitulos': self.subcapitulos,
            'tabs': self.tabs,
            'secciones': self.secciones,
            'subsecciones': self.subsecciones,
            'chunks': self.chunks
        }

    def get_and_save_chunks(self, WEBSITE_METADATA_FILE_PATH:str ,metadata:dict) -> dict[str, dict[str, Any]]:
        write_json(metadata, WEBSITE_METADATA_FILE_PATH)

        chunks = metadata["chunks"]
        logging.info(Fore.BLUE + f"Created {len(chunks)} chunks." + Style.RESET_ALL)

        return chunks

class PDFChunker(DocumentChunker):
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

    def get_and_save_chunks(self, PDF_METADATA_FILE_PATH:str , metadata: dict) -> dict[str, dict[str, Any]]:
        write_json(metadata, PDF_METADATA_FILE_PATH)

        chunks = metadata["chunks"]
        logging.info(Fore.BLUE + f"Created {len(chunks)} chunks." + Style.RESET_ALL)

        return chunks