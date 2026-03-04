# General
from colorama import Fore, Style
from abc import ABC, abstractmethod

# Helpers
from src.utils.prompts import build_generator_prompt
from src.utils.prompts import build_verifier_prompt
from src.utils.io import load_prompt

# Qdrant
from qdrant_client.models import ScoredPoint

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

class LLM_Engine(ABC):
    def __init__(self, LLM_SOURCE: str, groq_model: str, gemini_model: str, temperature: float = 0):
        self.llm_source = LLM_SOURCE.lower()
        # ChatGoogleGenerativeAI
        if self.llm_source == "google":     
            self.generator_model = gemini_model
        # ChatGroq
        elif self.llm_source == "groq":     
            self.generator_model = groq_model
        
        else:
            logging.info("Model {self.llm_source} not supported.")
            raise ValueError(f"Modelo {self.llm_source} no disponible.")
        
    async def call_generator_llm(self, prompt):
        if self.llm_source == "gemini":
            response = await self.generator_model.ainvoke(prompt)
            return response.content[0]["text"].strip()
        else:
            response = await self.generator_model.ainvoke(prompt)
            return response.content.strip()

    async def prompt_llm(self, user_message: str, contexto: str):
        generator_base_prompt = load_prompt("generate_prompt.txt")
        generator_prompt = build_generator_prompt(generator_base_prompt, user_message, contexto)
        generator_response = await self.call_generator_llm(generator_prompt)
        return generator_response


    def generate_context(self, vectors: list[ScoredPoint], textos: dict[str, str]) -> str:
        # General information for all chunks
        general_payload = vectors[0].payload
        context = f"""
            DOCUMENTO: {general_payload.get('doc_titulo', '').upper()}
            Resumen del documento: {general_payload.get('doc_resumen', '')}

            CAPÍTULO: {general_payload.get('cap_titulo', '').upper()}
            Descripción del capítulo: {general_payload.get('cap_texto', '')}
        """
        
        # Merge chunk information
        paragraphs = []
        for index, vector in enumerate(vectors):
            payload = vector.payload

            paragraph = f"""
            ---
            CHUNK {index+1}:


            TEXTO: {textos[payload["texto_id"]]}
            """.strip()

            paragraphs.append(paragraph)

        return context + "\n\n".join(paragraphs)

