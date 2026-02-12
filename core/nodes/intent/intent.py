# General
import re
import json
from typing import Any

# LangGraph
from core.models.state import ChatState

# Helpers
from core.nodes.intent.converter import convert_audio_to_text
from core.utils.io import load_prompt
from core.utils.io import load_json_schema
from core.utils.prompts import build_intention_prompt

# Classes
from core.intention.validator import TextValidator, AudioValidator

# Configution
from config.settings import MAX_TEXT_SIZE
from config.settings import MAX_AUDIO_SIZE
from config.settings import LLM_SOURCE
from config.settings import GROQ_GENERATOR_MODEL, GEMINI_GENERATOR_MODEL

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

def _build_prompt(user_message_text: str) -> str:
    # Load files
    system_base_prompt = load_prompt("intent_prompt.txt")
    answer_example = load_json_schema("schema_respuestas.json")
    intenciones_schema = load_json_schema("schema_intenciones.json")

    # Build prompt
    system_prompt = build_intention_prompt(system_base_prompt, intenciones_schema, answer_example, user_message_text)
    return system_prompt

def identify_intent(state: ChatState):
    # validate input
    if state["user_message_format"] == "text":
        validator = TextValidator(state["user_message"], format="text", max_size=MAX_TEXT_SIZE)
        user_message_text: str = validator.validate_input()
    elif format == "audio":
        validator = AudioValidator(state["user_message"], format="audio", max_size=MAX_AUDIO_SIZE)
        user_message_audio: bytes = validator.validate_input()

    # convert audio to text
    if format == "audio":
        user_message_text: str = convert_audio_to_text(user_message_audio)
    state["user_message_str"] = user_message_text

    # build prompt and call llm
    intent_prompt: str = _build_prompt(user_message_text)
    response_raw: str = _call_llm(intent_prompt)
    # response_obj: object = _extract_json_from_response(response_raw)
    print(response_raw)

    # update el estado
    

    return state 