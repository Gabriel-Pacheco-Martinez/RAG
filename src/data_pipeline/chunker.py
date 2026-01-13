import re
import uuid
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
    
    def __init__(self, document_id: int = 1042, author: str = "BNB", debug: bool = False):
        self.document_id = document_id
        self.author = author
        self.chapter_counter = 0
        self.section_counter = 0
        self.chunk_counter = 0
        self.debug = debug
    
    def chunk_document(self, document_text: str) -> Dict[str, Any]:
        """
        Parse document text and create hierarchical chunks.
        
        Args:
            document_text: The full text of the document
            
        Returns:
            Dict containing documents, chapters, sections, and chunks
        """
        if self.debug:
            print("=== DOCUMENT TEXT ===")
            print(document_text[:500])
            print("\n=== PROCESSING ===")
        
        lines = [line.strip() for line in document_text.split('\n') if line.strip()]
        
        if self.debug:
            print(f"Total lines: {len(lines)}")
            print("First 10 lines:")
            for i, line in enumerate(lines[:10]):
                print(f"{i}: {line}")
        
        # Initialize structure
        result = {
            "documents": {},
            "chapters": {},
            "sections": {},
            "chunks": {}
        }
        
        # Extract document title
        doc_title = "CAJAS DE AHORRO"
        for line in lines:
            if "CAJA" in line.upper() and "AHORRO" in line.upper():
                doc_title = line
                break
        
        # Parse the document into structured data
        chapters = self._parse_structure(lines)
        
        if self.debug:
            print(f"\nFound {len(chapters)} chapters")
            for ch in chapters:
                print(f"  Chapter: {ch['title']}, Sections: {len(ch['sections'])}")
        
        # Build the hierarchical structure
        chapter_ids = []
        
        for chapter_data in chapters:
            self.chapter_counter += 1
            chapter_id = self.chapter_counter
            chapter_ids.append(chapter_id)
            
            section_ids = []
            
            for section_data in chapter_data['sections']:
                self.section_counter += 1
                section_id = self.section_counter
                section_ids.append(section_id)
                
                chunk_ids = []
                chunk_index_in_section = 0
                
                for chunk_text in section_data['chunks']:
                    self.chunk_counter += 1
                    chunk_id = self.chunk_counter
                    chunk_ids.append(chunk_id)
                    chunk_index_in_section += 1
                    
                    # Add chunk
                    result['chunks'][str(chunk_id)] = {
                        "chunk_id": chunk_id,
                        "chunk_index": chunk_index_in_section,
                        "section_id": section_id,
                        "chapter_id": chapter_id,
                        "document_id": self.document_id,
                        "text": chunk_text
                    }
                
                # Add section
                result['sections'][str(section_id)] = {
                    "title": section_data['title'],
                    "chapter_id": chapter_id,
                    "chunks": chunk_ids,
                    "section_index": len(section_ids)
                }
            
            # Add chapter
            result['chapters'][str(chapter_id)] = {
                "title": chapter_data['title'],
                "sections": section_ids,
                "document_id": self.document_id
            }
        
        # Add document
        result['documents'][str(self.document_id)] = {
            "title": doc_title,
            "author": self.author,
            "chapters": chapter_ids
        }
        
        return result
    
    def _parse_structure(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse lines into chapters with sections and chunks."""
        chapters = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detect chapter titles
            if self._is_chapter_title(line):
                if self.debug:
                    print(f"\nFound chapter at line {i}: {line}")
                
                chapter_title = line
                i += 1
                
                # Parse sections within this chapter
                sections, i = self._parse_sections(lines, i)
                
                chapters.append({
                    'title': chapter_title,
                    'sections': sections
                })
            else:
                i += 1
        
        return chapters
    
    def _parse_sections(self, lines: List[str], start_idx: int) -> Tuple[List[Dict[str, Any]], int]:
        """Parse sections within a chapter until the next chapter starts."""
        sections = []
        i = start_idx
        
        while i < len(lines):
            line = lines[i]
            
            # Stop if we hit another chapter
            if self._is_chapter_title(line):
                break
            
            # Detect section titles
            if self._is_section_title(line):
                if self.debug:
                    print(f"  Found section at line {i}: {line}")
                
                section_title = line
                i += 1
                
                # Parse chunks within this section
                chunks, i = self._parse_chunks(lines, i, section_title)
                
                if self.debug:
                    print(f"    Extracted {len(chunks)} chunks")
                
                sections.append({
                    'title': section_title,
                    'chunks': chunks
                })
            else:
                i += 1
        
        return sections, i
    
    def _parse_chunks(self, lines: List[str], start_idx: int, section_title: str) -> Tuple[List[str], int]:
        """Parse chunks within a section until the next section/chapter starts."""
        chunks = []
        i = start_idx
        description_buffer = []
        
        while i < len(lines):
            line = lines[i]
            
            # Stop if we hit a section or chapter title
            if self._is_section_title(line) or self._is_chapter_title(line):
                # Save any buffered description
                if description_buffer and section_title == "Descripción":
                    chunks.append(" ".join(description_buffer))
                break
            
            # Special handling for Descripción section
            if section_title == "Descripción":
                chunk = self._extract_description_chunk(line, description_buffer)
                if chunk:
                    chunks.append(chunk)
                    description_buffer = []
                elif line and not self._should_skip_line(line):
                    description_buffer.append(line)
            
            # Special handling for Requisitos section
            elif section_title == "Requisitos":
                chunk = self._extract_requisito_chunk(line)
                if chunk:
                    chunks.append(chunk)
            
            i += 1
        
        # Save any remaining description
        if description_buffer and section_title == "Descripción":
            chunks.append(" ".join(description_buffer))
        
        return chunks, i
    
    def _is_chapter_title(self, line: str) -> bool:
        """Check if line is a chapter title."""
        # More flexible matching
        return bool(re.match(r'^BANCA\s+(JOVEN|SENIOR)', line, re.IGNORECASE))
    
    def _is_section_title(self, line: str) -> bool:
        """Check if line is a section title."""
        # More flexible matching including typos
        return line in ["Descripción", "Características", "Carácterísticas", "Requisitos"]
    
    def _should_skip_line(self, line: str) -> bool:
        """Check if line should be skipped."""
        skip_keywords = [
            "Haz crecer",
            "Elige la forma",
            "Cuenta unipersonal",
            "Es una cuenta",
            "Contact Center",
            "Call Center",
            "Cédula de identidad u otro documento"
        ]
        
        # Skip bullets
        if line.startswith('•'):
            return True
        
        # Skip lines with skip keywords
        for keyword in skip_keywords:
            if keyword.lower() in line.lower():
                return True
        
        return False
    
    def _extract_description_chunk(self, line: str, buffer: List[str]) -> str:
        """Extract description chunk."""
        # If we have a complete description paragraph
        if re.match(r'^La Caja de Ahorros', line):
            # This is the start of a description
            return ""
        
        # Check if this completes a description (ends with period and mentions key info)
        if buffer and line.endswith('.') and ('país' in line.lower() or 'mensualmente' in line.lower()):
            buffer.append(line)
            return " ".join(buffer)
        
        return ""
    
    def _extract_requisito_chunk(self, line: str) -> str:
        """Extract requisito chunk."""
        # Extract age requirement
        age_match = re.search(r'Personas\s+[nN]aturales\s+de\s+(\d+)(?:\s+a\s+(\d+))?\s+años', line)
        if age_match:
            if age_match.group(2):
                return f"Personas naturales de {age_match.group(1)} a {age_match.group(2)} años."
            else:
                return f"Personas naturales de {age_match.group(1)} años o más."
        
        # Extract minimum opening amount
        amount_match = re.search(r'Monto\s+mínimo\s+de\s+apertura[:\s]*Bs\.?\s*(\d+)', line, re.IGNORECASE)
        if amount_match:
            return f"Monto mínimo de apertura de Bs {amount_match.group(1)}."
        
        return ""