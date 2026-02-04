# General
import json
import logging
import re
from typing import Dict, Any
from abc import ABC, abstractmethod

# Methods
from src.utils.io import load_prompt
from src.utils.io import load_schema
from src.utils.prompts import build_intention_prompt

# Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from config.settings import PROMPTS_INTENT_PATH

logger = logging.getLogger(__name__)

class Client(ABC):
    """
    Abstract class for LLM clients
    """
    def __init__(self, MODEL: str, KEY: str, LLM_SOURCE: str = "groq"):
        self.model = MODEL
        self.key = KEY
        self.llm_source = LLM_SOURCE

    @abstractmethod
    def get_intent(self):
        pass

    def _parse_llm_answer(self, llm_answer: str) -> Dict[str, Any]:
        try:
            return json.loads(llm_answer)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON block with regex
        json_match = re.search(r"\{.*\}", llm_answer, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Fallback if nothing worked
        return {"intencion": "nula", "entidades": {}}
        
class GeminiClient(Client):
    def __init__(self, MODEL: str, KEY: str, LLM_SOURCE: str = "groq"):
        super().__init__(MODEL, KEY, LLM_SOURCE)
        # self.llm_model = ChatGoogleGenerativeAI(model=MODEL, temperature=0.3, google_api_key=KEY)
        self.llm_model = ChatGroq(model=MODEL, temperature=0.3, api_key=KEY)

    def call_intent_llm(self, prompt):
        if self.llm_source == "gemini":
            response = self.llm_model.invoke(prompt).content[0]["text"].strip()
        else:
            response = self.llm_model.invoke(prompt).content.strip().lower()
        return response

    def _llm_intent(self, user_message: str, memory: dict) -> Dict[str, Any]:
        system_base_prompt = load_prompt(PROMPTS_INTENT_PATH, "intent_prompt.txt")
        answer_example = load_schema("schema_respuestas.json")
        intenciones_schema = load_schema("schema_intenciones.json")

        system_prompt = build_intention_prompt(system_base_prompt, intenciones_schema, memory, answer_example, user_message)
        
        intent_response = self.call_intent_llm(system_prompt)
        intent_response = self._parse_llm_answer(intent_response)

        logging.info(f"LLMs prompted and responses returned")
        return intent_response
        
    def get_intent(self, user_message: str, memory: Dict[str, Any]) -> Dict[str, Any]:
        return self._llm_intent(user_message, memory)
