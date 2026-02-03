# General
import json
import pprint
import re
from typing import Dict, Any
from abc import ABC, abstractmethod

# Methods
from src.utils.io import load_prompt
from src.utils.io import load_schema


# Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from config.settings import PROMPTS_INTENT_PATH


class Client(ABC):
    """
    Abstract class for LLM clients
    """
    def __init__(self, MODEL: str, KEY: str, CHATBOT_MENU_SET: dict):
        self.model = MODEL
        self.key = KEY
        self.chatbot_menu_set = CHATBOT_MENU_SET

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
    def __init__(self, MODEL: str, KEY: str, CHATBOT_MENU_SET: set):
        super().__init__(MODEL, KEY, CHATBOT_MENU_SET)
        # self.llm_model = ChatGoogleGenerativeAI(model=MODEL, temperature=0.3, google_api_key=KEY)
        self.llm_model = ChatGroq(model=MODEL, temperature=0.3, api_key=KEY)

    def _llm_intent(self, user_message: str, memory: dict) -> Dict[str, Any]:
        system_prompt = load_prompt(PROMPTS_INTENT_PATH, "intent_prompt.txt")
        answer_schema = load_schema("schema_respuestas.json")
        intenciones_schema = load_schema("schema_intenciones.json")

        # Build prompt
        llm_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template("Mensaje de usuario:\n{message_placeholder}")
        ])
        llm_prompt = llm_prompt.invoke({
            "intenciones_schema": json.dumps(intenciones_schema, indent=2, ensure_ascii=False),
            "memoria": json.dumps(memory, indent=2, ensure_ascii=False),
            "ejemplo": json.dumps(answer_schema, indent=2, ensure_ascii=False),
            "message_placeholder": user_message
        })

        # Invoke llm response
        llm_answer = self.llm_model.invoke(llm_prompt).content.strip().lower()
        return self._parse_llm_answer(llm_answer), llm_prompt.to_string().splitlines()

    def get_intent(self, user_message: str, memory: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hybrid approach: rule-based first, LLM fallback
        """

        # =======
        # LLM-based detection
        return self._llm_intent(user_message, memory)
    