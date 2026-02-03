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


from src.utils.io import read_json, load_prompt

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
        generator_base_prompt = load_prompt("generate_prompt.txt")
        verifier_base_prompt = load_prompt("verify_prompt.txt")

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

class LLM_Engine_PDFs(LLM_Engine):
    def __init__(self, LLM_SOURCE: str, config: dict,  metadata_file_path: str,temperature: float = 0):
        super().__init__(LLM_SOURCE, config, temperature)
        self.metadata = read_json(metadata_file_path)

    def generate_context(self, context_vectors: list[dict]):
        # Get chunk_ids from retrieved vectors
        chunk_ids = [cv["chunk_id"] for cv in context_vectors]

        # Get metadata 
        chunks = self.metadata["chunks"]
        sections = self.metadata["sections"]
        chapters = self.metadata["chapters"]

        # Get chapter_id and section_id for vectors
        chapter_ids = []
        section_ids = []
        for cid in chunk_ids:
            chunk = chunks[str(cid)]
            chapter_ids.append(chunk["chapter_id"])
            section_ids.append(chunk["section_id"])
                    
        # Get the most common chapter and section
        most_common_chapter = Counter(chapter_ids).most_common(1)[0][0]
        most_common_section = Counter(section_ids).most_common(1)[0][0]

         # Get chapter title
        chapter_title = chapters[str(most_common_chapter)]["title"]

        # Get all section titles for that chapter
        section_titles = [
            sections[str(sid)]["title"] 
            for sid in chapters[str(most_common_chapter)]["sections"]
        ]

        # List of text for most common chapter
        chapter_chunks = [ 
            c["text"] for c in chunks.values()
            if c["chapter_id"] == most_common_chapter
        ]

        # Join all text for most common chapter
        chapter_context = " ".join(chapter_chunks)

        # Chapter title + section title + chapter context for LLM 
        context_for_llm = f"Capitulo: {chapter_title}\nSecciones incluidas: {', '.join(section_titles)}\n\n{chapter_context}"

        # Say something
        logging.info(Fore.BLUE + f"Created a context of {len(context_for_llm.split())} words for the LLM." + Style.RESET_ALL)
        return context_for_llm