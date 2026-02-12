# General
from colorama import Fore, Style
from abc import ABC, abstractmethod

# Helpers
from core.utils.prompts import build_generator_prompt
from core.utils.prompts import build_verifier_prompt
from core.utils.io import load_prompt

# Logging
import logging
logger = logging.getLogger(__name__)

class LLM_Engine(ABC):
    def __init__(self, LLM_SOURCE: str, groq_model: str, gemini_model: str, temperature: float = 0):
        self.llm_source = LLM_SOURCE.lower()
        
        # ChatGoogleGenerativeAI
        if self.llm_source == "gemini":     
            self.generator_model = gemini_model
            self.verifier_model = gemini_model
        
        # ChatGroq
        elif self.llm_source == "groq":     
            self.generator_model = groq_model
            self.verifier_model = groq_model
        
        else:
            raise ValueError(f"Model {self.llm_source} not supported")
        
    def call_generator_llm(self, prompt):
        if self.llm_source == "gemini":
            response = self.generator_model.invoke(prompt).content[0]["text"].strip()
        else:
            response = self.generator_model.invoke(prompt).content.strip()
        return response
    
    def call_verifier_llm(self, prompt):
        if self.llm_source == "gemini":
            response = self.verifier_model.invoke(prompt).content[0]["text"].strip()
        else:
            response = self.verifier_model.invoke(prompt).content.strip()
        return response

    def prompt_llm(self, user_message: str, contexto: str):
        generator_base_prompt = load_prompt("generate_prompt.txt")
        verifier_base_prompt = load_prompt("verify_prompt.txt")

        generator_prompt = build_generator_prompt(generator_base_prompt, user_message, contexto)
        verifier_prompt = build_verifier_prompt(verifier_base_prompt, user_message, contexto)

        generator_response = self.call_generator_llm(generator_prompt)
        verifier_response = self.call_verifier_llm(verifier_prompt)

        logging.info(f"LLMs prompted and responses returned")
        return generator_response


    def generate_context(self, vector: dict) -> str:
        payload = vector.payload

        context = f"""
        DOCUMENTO: {payload.get('doc_titulo', '').upper()}
        Resumen del documento:
        {payload.get('doc_resumen', '')}

        CAPÍTULO: {payload.get('cap_titulo', '').upper()}
        Descripción del capítulo:
        {payload.get('cap_texto', '')}

        CONTENIDO RELEVANTE:
        {payload.get('texto', '')}

        """.strip()

        return context

