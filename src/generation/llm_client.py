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

from src.utils.prompts import load_prompt

class LLM_Engine():
    def __init__(self, LLM_ANSWER_MODEL: str, LLM_VERIFY_MODEL: str, metadata_path: str):
        self.llm_answer_model = LLM_ANSWER_MODEL
        self.llm_verify_model = LLM_VERIFY_MODEL

        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    @staticmethod
    def get_llm(model_name: str, temperature=0) -> object:
        """
        Return the appropiate LLM object based on
        the model chosen. At the moment the options are:
            * qwen      -> ChatOllama
            * groq      -> ChatGroq
            * gemini    -> ChatGoogleGenerativeAI
        """
        if model_name == "qwen":
            return ChatOllama(model="qwen3:8b", temperature=temperature)
        elif model_name == "groq":
            return ChatGroq(model="llama-3.1-8b-instant", temperature=temperature, api_key=os.environ["GROQ_API_KEY"])
        elif model_name == "gemini":
            return ChatGoogleGenerativeAI("gemini-3-pro-preview", temperature=temperature, google_api_key=os.environ["GEMINI_API_KEY"])
        else:
            raise ValueError(f"Model {model_name} not supported")

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
        print(f"\033[34mCreated a context of {len(context_for_llm.split())} words for the LLM.\033[0m")
        return context_for_llm

    def prompt_llm(self, context: str, user_query: str):
        # =======
        # 1. Load system prompts
        primary_llm_sys_prompt = load_prompt("prompt.txt")
        secondary_llm_sys_prompt = load_prompt("verify_prompt.txt")

        # =======
        # 2. Build ANSWER prompt (role-aware)
        answer_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(primary_llm_sys_prompt),
            SystemMessagePromptTemplate.from_template("Contexto:\n{context}"), #These {} are placeholders only
            HumanMessagePromptTemplate.from_template("{question}")
        ])
        
        # ======
        # 3. Build VERIFY prompt (role-aware)
        verify_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(secondary_llm_sys_prompt),
            SystemMessagePromptTemplate.from_template("Contexto:\n{context}"),
            SystemMessagePromptTemplate.from_template("Respuesta a evaluar:\n{llm_answer}")
        ])

        # ======
        # 4. Initialize LLMs
        answer_llm = self.get_llm(self.llm_answer_model)
        verifier_llm = self.get_llm(self.llm_verify_model)


        answer_llm = ChatOllama(model="qwen3:8b", temperature=0)
        verifier_llm = ChatOllama(model="qwen2.5:7b", temperature=0) # Change to smaller model

        # ======
        # 5. Invoke Answer LLM
        answer_message = answer_prompt.invoke({
            "context": context, # Change placeholders
            "question": user_query
        })
        answer_response = answer_llm.invoke(answer_message).content.strip()
        
        # ======
        # 6. Invoke Verify LLM
        verify_message = verify_prompt.invoke({
            "context": context,
            "llm_answer": answer_response
        })
        verify_response = verifier_llm.invoke(verify_message).content.strip()

        # ======
        # 7. Say something
        print(f"\033[34mLLMs prompted and responses returned.\033[0m")
        return {
            "answer": answer_response,
            "verify": verify_response,
            "context": context
        }


