# General
import re
import json
from typing import Any

# LangGraph
from src.models.state import ChatState

# Helpers
from src.nodes.intent.converter import convert_audio_to_text
from src.utils.io import load_prompt
from src.utils.io import load_json_schema
from src.utils.prompts import build_intention_prompt

# Classes
from src.validation.validator import TextValidator, AudioValidator

# Configution
from config.settings import MAX_TEXT_SIZE
from config.settings import MAX_AUDIO_SIZE
from config.settings import LLM_SOURCE
from config.settings import GROQ_GENERATOR_MODEL, GEMINI_GENERATOR_MODEL

def _extract_json_from_response(text: str) -> dict:
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found")

    brace_count = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                json_str = text[start:i+1]
                return json.loads(json_str)

    raise ValueError("No complete JSON object found")

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

def intent_detect(state: ChatState):
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
    response_obj: object = _extract_json_from_response(response_raw)

    # update el estado
    state["llm_intent_response"] = response_obj["intencion_actual"]
    state["intent_confidence"] = response_obj["confianza_en_la_intencion"]
    state["slots"] = response_obj["slots_requeridos"]

    # Say something
    print("🦺 INTENTION DETECTED LLM: DONE")
    return state