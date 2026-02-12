# LangGraph
import re
import json
from core.models.state import ChatState

# LangChain
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Helpers
from core.utils.io import load_prompt, load_yaml_schema

# Configuration
from config.settings import LLM_SOURCE
from config.settings import GROQ_GENERATOR_MODEL, GEMINI_GENERATOR_MODEL

# Logging 
import logging
logger = logging.getLogger(__name__)

def _extract_json_from_response(text: str) -> dict:
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")
    
    json_str = match.group(0)

    # Remove trailing commas before } or ]
    json_str = re.sub(r",\s*([}\]])", r"\1", json_str)

    return json.loads(json_str)

def _call_llm(state: ChatState, prompt: str) -> str:
    if LLM_SOURCE == "groq":
        return GROQ_GENERATOR_MODEL.invoke(prompt).content.strip()
    elif LLM_SOURCE == "gemini":
        return GEMINI_GENERATOR_MODEL.invoke(prompt).content[0]["text"].strip()

def _build_classify_prompt(state: ChatState, _classify_base_prompt: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(_classify_base_prompt),
        HumanMessagePromptTemplate.from_template("Mensaje de usuario:\n{user_message_ph}")
    ])

    prompt = prompt.invoke({
        "temas": json.dumps(load_yaml_schema("topics.yaml")), # dict
        "tema_previo": state["topic_previous"],
        "memoria_conversacion": json.dumps(state["conversation_history"]), # list
        "contexto_rag": state["context"],
        "user_message_ph": state["user_message"],
    })

    return prompt

def _update_state(state: ChatState, response: str):
    state["topic"] = response["topic"]
    state["topic_confidence"] = response["topic_confidence"]
    state["user_message_ambiguos"] = response["user_message_ambiguos"]
    state["is_follow_up"] = response["is_follow_up"]
    state["rewritten_query"] = response["rewritten_query"]
    return state

def classify_query(state: ChatState) -> dict:
    # Armar prompt
    classify_base_prompt = load_prompt("classify_prompt.txt")
    classify_prompt = _build_classify_prompt(state, classify_base_prompt)

    # Llamar al LLM
    response_raw = _call_llm(state, classify_prompt)
    print(response_raw)
    response_obj = _extract_json_from_response(response_raw)
    print(response_obj)
    state["llm_topic_response"] = response_obj["rewritten_query"]
    logger.info(f"LLM Topic llamado. La respuesta es: {response_raw}")
    
    # Update el estado
    state = _update_state(state, response_obj)

    return state