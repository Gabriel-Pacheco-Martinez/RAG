import re
import uuid
from abc import ABC, abstractmethod

class DocumentChunker(ABC):
    @abstractmethod
    def chunk_document(self, document_text):
        pass
class PDFDocumentChunker(DocumentChunker):
    TITLE = {"CAJAS DE AHORRO"}

    SECTION_TITLES = {
        "BANCA JOVEN",
        "BANCA ACTIVA",
        "BANCA SENIOR"
    }

    SUBSECTIONS = {
        "Descripción",
        "Beneficios",
        "Características",
        "Requisitos",
        "Tasa de Interés de acuerdo al siguiente esquema:"
    }

    def chunk_document(self, document_text):
        # Split text into non-empty stripped lines
        lines = [l.strip() for l in document_text.splitlines() if l.strip()]
        stack = []  # stack will hold element_ids
        chunks = []
        current_content_lines = []  # buffer to accumulate multi-line content

        # Print lines with their index for debugging
        print("Printing lines with their index:")
        for idx, line in enumerate(lines):
            print(f"{idx}: {line}")

        def flush_content():
            """Flush accumulated content as a single chunk"""
            if current_content_lines:
                element_id = str(uuid.uuid4())
                parent_id = stack[-1] if stack else None
                chunks.append({
                    "type": "content",
                    "element_id": element_id,
                    "text": "\n".join(current_content_lines),
                    "metadata": {
                        "level": 3,
                        "page_number": None,
                        "filetype": "pdf",
                        "parent_id": parent_id
                    }
                })
                current_content_lines.clear()

        for line in lines:
            upper_line = line.upper()

            # --- TITLE ---
            if upper_line in self.TITLE:
                stack.clear()           # reset stack for new title
                flush_content()
                element_id = str(uuid.uuid4())
                chunks.append({
                    "type": "title",
                    "element_id": element_id,
                    "text": line,
                    "metadata": {
                        "level": 0,
                        "page_number": None,
                        "filetype": "pdf",
                        "parent_id": None
                    }
                })
                stack.append(element_id)  # push title id to stack

            # --- SECTION TITLE ---
            elif upper_line in self.SECTION_TITLES:
                # Pop until only the title remains
                while len(stack) > 1:
                    stack.pop()
                flush_content()
                element_id = str(uuid.uuid4())
                parent_id = stack[-1] if stack else None
                chunks.append({
                    "type": "section_title",
                    "element_id": element_id,
                    "text": line,
                    "metadata": {
                        "level": 1,
                        "page_number": None,
                        "filetype": "pdf",
                        "parent_id": parent_id
                    }
                })
                stack.append(element_id)  # push section id

            # --- SUBSECTION TITLE ---
            elif line in self.SUBSECTIONS:
                # Pop until only title + section remain
                while len(stack) > 2:
                    stack.pop()
                flush_content()
                element_id = str(uuid.uuid4())
                parent_id = stack[-1] if stack else None
                chunks.append({
                    "type": "subsection_title",
                    "element_id": element_id,
                    "text": line,
                    "metadata": {
                        "level": 2,
                        "page_number": None,
                        "filetype": "pdf",
                        "parent_id": parent_id
                    }
                })
                stack.append(element_id)  # push subsection id

            # --- CONTENT ---
            else:
                current_content_lines.append(line)

        # Flush any remaining content at the end
        flush_content()

        return chunks