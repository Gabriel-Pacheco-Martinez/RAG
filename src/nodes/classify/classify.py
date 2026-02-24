# LangGraph
import re
import json
from src.models.state import ChatState

# LangChain
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Helpers
from src.utils.io import load_prompt
from src.utils.prompts import build_classify_prompt

# Configuration
from config.settings import LLM_SOURCE
from config.settings import GROQ_GENERATOR_MODEL, GEMINI_GENERATOR_MODEL

# Logging 
import logging
logger = logging.getLogger(__name__)


def _update_state(state: ChatState, response: str):
    state["topic"] = response["topic"]
    state["topic_confidence"] = response["topic_confidence"]
    state["user_message_ambiguous"] = response["user_message_ambiguous"]
    state["is_follow_up"] = response["is_follow_up"]
    state["rewritten_query"] = response["rewritten_query"]
    if state["is_follow_up"]:
        state["info_source"] = "memory"
    else:
        state["info_source"] = "rag"
    return state

def _extract_json_from_response(text: str) -> dict:
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")
    
    json_str = match.group(0)

    # Remove trailing commas before } or ]
    json_str = re.sub(r",\s*([}\]])", r"\1", json_str)

    return json.loads(json_str)

def _call_llm(prompt: str) -> str:
    if LLM_SOURCE == "groq":
        return GROQ_GENERATOR_MODEL.invoke(prompt).content.strip()
    elif LLM_SOURCE == "gemini":
        return GEMINI_GENERATOR_MODEL.invoke(prompt).content[0]["text"].strip()

def classify_query(state: ChatState) -> dict:
    # Armar prompt
    classify_base_prompt = load_prompt("classify_prompt.txt")
    classify_prompt = build_classify_prompt(state, classify_base_prompt)

    # Llamar al LLM
    response_raw: str = _call_llm(classify_prompt)
    response_obj: object = _extract_json_from_response(response_raw)
    logger.info(f"LLM Topic llamado. La respuesta es: {response_raw}")

    # Update el estado
    state = _update_state(state, response_obj)

    # Say something
    print("🦺 CLASSIFICATION LLM: DONE")

    return state