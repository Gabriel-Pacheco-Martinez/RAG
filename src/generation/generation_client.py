# General
import logging
import pprint
from colorama import Fore, Style

from abc import ABC, abstractmethod

import json
import os
from collections import Counter
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.prompts import build_generator_prompt, build_verifier_prompt
from config.settings import PROMPTS_GENERATION_PATH


from src.utils.io import read_json, load_prompt

logger = logging.getLogger(__name__)

class LLM_Engine(ABC):
    def __init__(self, LLM_SOURCE: str, config: dict, temperature: float = 0):
        self.llm_source = LLM_SOURCE.lower()
        
        # ChatGoogleGenerativeAI
        if self.llm_source == "gemini":     
            self.generator_model = ChatGoogleGenerativeAI(model=config["LLM_GENERATOR_MODEL_GEMINI"], temperature=temperature, google_api_key=os.environ["GEMINI_API_KEY"])
            self.verifier_model = ChatGoogleGenerativeAI(model=config["LLM_VERIFY_MODEL_GEMINI"], temperature=temperature, google_api_key=os.environ["GEMINI_API_KEY"])
        
        # ChatOllama
        elif self.llm_source == "ollama":   
            self.generator_model = ChatOllama(model=config["LLM_GENERATOR_MODEL_OLLAMA"], temperature=temperature)
            self.verifier_model = ChatOllama(model=config["LLM_VERIFY_MODEL_OLLAMA"], temperature=temperature)
        
        # ChatGroq
        elif self.llm_source == "groq":     
            self.generator_model = ChatGroq(model=config["LLM_GENERATOR_MODEL_GROQ"], temperature=temperature, api_key=os.environ["GROQ_API_KEY"])
            self.verifier_model = ChatGroq(model=config["LLM_VERIFY_MODEL_GROQ"], temperature=temperature, api_key=os.environ["GROQ_API_KEY"])
        
        else:
            raise ValueError(f"Model {self.llm_source} not supported")
        
    @abstractmethod
    def generate_context(self, context_vectors: list[dict]):
        pass

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
        generator_base_prompt = load_prompt(PROMPTS_GENERATION_PATH, "generate_prompt.txt")
        verifier_base_prompt = load_prompt(PROMPTS_GENERATION_PATH, "verify_prompt.txt")

        generator_prompt = build_generator_prompt(generator_base_prompt, user_message, contexto)
        verifier_prompt = build_verifier_prompt(verifier_base_prompt, user_message, contexto)

        generator_response = self.call_generator_llm(generator_prompt)
        verifier_response = self.call_verifier_llm(verifier_prompt)

        logging.info(f"LLMs prompted and responses returned")
        return {
            "answer": generator_response,
            "verify": verifier_response,
            "context": contexto
        }

class LLM_Engine(LLM_Engine):
    def __init__(self, LLM_SOURCE: str, config: dict, temperature: float = 0):
        super().__init__(LLM_SOURCE, config, temperature)

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
