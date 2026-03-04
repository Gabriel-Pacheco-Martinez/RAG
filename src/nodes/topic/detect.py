# General 
from colorama import Fore, Style
from time import perf_counter

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
logger = logging.getLogger('uvicorn.error')


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
    start = text.find("{")
    if start == -1:
        logging.info("[X] No JSON object found on INTENTION DETECTION LLM response")
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

    logging.info("[X] No complete JSON object found on INTENTION DETECTION LLM response")
    raise ValueError("No complete JSON object found")

async def _call_llm(prompt: str) -> str:
    if LLM_SOURCE == "groq":
        response = await GROQ_GENERATOR_MODEL.ainvoke(prompt)
        return response.content.strip()
    elif LLM_SOURCE == "gemini":
        response = await GEMINI_GENERATOR_MODEL.ainvoke(prompt)
        return response.content[0]["text"].strip()

async def topic_detect(state: ChatState) -> dict:
    # Timer
    state["start_timer_topic"] = perf_counter()

    logger.info(Fore.RED + f"{state['user_session_id']}: " + Style.RESET_ALL + f"{state['user_message']}")

    # Armar prompt
    classify_base_prompt = load_prompt("classify_prompt.txt")
    classify_prompt = build_classify_prompt(state, classify_base_prompt)
    response_raw: str = await _call_llm(classify_prompt)
    response_obj: object = _extract_json_from_response(response_raw)
    logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + "[✅] 👾 TOPIC DETECTED: " + Style.RESET_ALL + "it took " + Fore.YELLOW + f"{perf_counter() - state['start_timer_topic']:.4f}s ⏱. " + Style.RESET_ALL + f"{response_obj}")

    # Update el estado
    state = _update_state(state, response_obj)

    # Say something
    return state