# General 
import json

# Classes
from langchain_core.prompt_values import PromptValue
from typing import Awaitable

# Configuration
from config.settings import LLM_SOURCE
from config.settings import GROQ_GENERATOR_MODEL, GEMINI_GENERATOR_MODEL

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

async def call_llm(prompt: PromptValue) -> Awaitable[str]:
    response_text = ""
    if LLM_SOURCE == "groq":
        response = await GROQ_GENERATOR_MODEL.ainvoke(prompt)
        response_text = response.content.strip()
    elif LLM_SOURCE == "gemini":
        response = await GEMINI_GENERATOR_MODEL.ainvoke(prompt)
        response_text = response.content[0]["text"].strip()
    return response_text

def extract_json_from_response(text: Awaitable[str]) -> dict:
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