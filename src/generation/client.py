# General
import logging
import pprint
from colorama import Fore, Style

import json
import os
from collections import Counter
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from src.utils.io import load_prompt

class LLM_Engine():
    def __init__(self, LLM_SOURCE: str, config: dict, metadata_path: str, temperature: float = 0):
        # Initialize needed models
        self.llm_source = LLM_SOURCE.lower()
        if self.llm_source == "gemini":     # ChatGoogleGenerativeAI
            self.answer_llm = ChatGoogleGenerativeAI(model=config["LLM_ANSWER_MODEL_GEMINI"], temperature=temperature, google_api_key=os.environ["GEMINI_API_KEY"])
            self.verifier_llm = ChatGoogleGenerativeAI(model=config["LLM_VERIFY_MODEL_GEMINI"], temperature=temperature, google_api_key=os.environ["GEMINI_API_KEY"])
        elif self.llm_source == "ollama":   # ChatOllama
            self.answer_llm = ChatOllama(model=config["LLM_ANSWER_MODEL_OLLAMA"], temperature=temperature)
            self.verifier_llm = ChatOllama(model=config["LLM_VERIFY_MODEL_OLLAMA"], temperature=temperature)
        elif self.llm_source == "groq":     # ChatGroq
            self.answer_llm = ChatGroq(model=config["LLM_ANSWER_MODEL_GROQ"], temperature=temperature, api_key=os.environ["GROQ_API_KEY"])
            self.verifier_llm = ChatGroq(model=config["LLM_VERIFY_MODEL_GROQ"], temperature=temperature, api_key=os.environ["GROQ_API_KEY"])
        else:
            raise ValueError(f"Model {self.llm_source} not supported")
        
        # Metadata loading
        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

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

    def prompt_gemini(self, context, user_query):
        # =======
        # Build ANSWER and VERIFY prompts (role-aware)
        answer_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.primary_llm_sys_prompt),
            SystemMessagePromptTemplate.from_template("Contexto:\n{context}"), # These {} are placeholders only
            HumanMessagePromptTemplate.from_template("Pregunta:\n{question}")
        ])
        
        verify_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.secondary_llm_sys_prompt),
            SystemMessagePromptTemplate.from_template("Contexto:\n{context}"),
            HumanMessagePromptTemplate.from_template("Respuesta a evaluar:\n{llm_answer}") # This has to change for gemini to Human
        ])

        # =======
        # Invoke ANSWER and VERIFY LLMs
        answer_message = answer_prompt.invoke({
            "context": context, # Change placeholders
            "question": user_query
        })
        answer_response = self.answer_llm.invoke(answer_message).content[0]["text"].strip()
        
        verify_message = verify_prompt.invoke({
            "context": context,
            "llm_answer": answer_response
        })
        verify_response = self.verifier_llm.invoke(verify_message).content[0]["text"].strip()

        # =======
        # Return
        return answer_response, verify_response
    
    def prompt_ollama_and_groq(self, context, user_query):
                # =======
        # Build ANSWER and VERIFY prompts (role-aware)
        answer_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.primary_llm_sys_prompt),
            SystemMessagePromptTemplate.from_template("Contexto:\n{context}"), # These {} are placeholders only
            HumanMessagePromptTemplate.from_template("Pregunta:\n{question}")
        ])
        
        verify_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.secondary_llm_sys_prompt),
            SystemMessagePromptTemplate.from_template("Contexto:\n{context}"),
            SystemMessagePromptTemplate.from_template("Respuesta a evaluar:\n{llm_answer}") # This has to change for gemini to Human
        ])

        # =======
        # Invoke ANSWER and VERIFY LLMs
        answer_message = answer_prompt.invoke({
            "context": context, # Change placeholders
            "question": user_query
        })
        answer_response = self.answer_llm.invoke(answer_message).content.strip()
        
        verify_message = verify_prompt.invoke({
            "context": context,
            "llm_answer": answer_response
        })
        verify_response = self.verifier_llm.invoke(verify_message).content.strip()

        # =======
        # Return
        return answer_response, verify_response

    def prompt_llm(self, context: str, user_query: str):        
        # Load system prompts text
        self.primary_llm_sys_prompt = load_prompt("prompt.txt")
        self.secondary_llm_sys_prompt = load_prompt("verify_prompt.txt")

        # Call llm
        if self.llm_source == "gemini":
            answer_response, verify_response = self.prompt_gemini(context, user_query)
        elif self.llm_source == "ollama" or self.llm_source == "groq":
            answer_response, verify_response = self.prompt_ollama_and_groq(context, user_query)

        # ======
        # 7. Say something
        logging.info(Fore.BLUE + f"LLMs prompted and responses returned." + Style.RESET_ALL)
        return {
            "answer": answer_response,
            "verify": verify_response,
            "context": context
        }
    