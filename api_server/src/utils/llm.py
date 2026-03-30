# General 
import json
from colorama import Fore, Style

# Classes
from langchain_core.prompt_values import PromptValue
from typing import Awaitable

# LangGraph
from src.models.state import ChatState

# Configuration
from config.enums import LLMSource
from config.settings import settings
from config.settings import GROQ_GENERATOR_MODEL 
from config.settings import GEMINI_GENERATOR_MODEL
from config.settings import OLLAMA_GENERATOR_MODEL

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

async def call_llm(state: ChatState, prompt: PromptValue) -> str:
    response_text = ""
    if  settings.LLM_SOURCE == LLMSource.GROQ:
        logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + " ☁️🍊 LLM SOURCE USED: " + Style.RESET_ALL + f"{settings.LLM_SOURCE}")
        response = await GROQ_GENERATOR_MODEL.ainvoke(prompt)
        state["token_count_input"] = state["token_count_input"] + response.response_metadata.get("token_usage").get("prompt_tokens")
        state["token_count_output"] = state["token_count_output"] + response.response_metadata.get("token_usage").get("completion_tokens")
        response_text = response.content.strip()
    elif settings.LLM_SOURCE == LLMSource.GOOGLE:
        logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + " ☁️📊 LLM SOURCE USED: " + Style.RESET_ALL + f"{settings.LLM_SOURCE}")
        response = await GEMINI_GENERATOR_MODEL.ainvoke(prompt)
        state["token_count_input"] = state["token_count_input"] + response.response_metadata.get("token_usage").get("prompt_tokens")
        state["token_count_output"] = state["token_count_output"] + response.response_metadata.get("token_usage").get("completion_tokens")
        response_text = response.content.strip()
    elif settings.LLM_SOURCE == LLMSource.OLLAMA:
        logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + " ☁️🦙 LLM SOURCE USED: " + Style.RESET_ALL + f"{settings.LLM_SOURCE}")
        response = await OLLAMA_GENERATOR_MODEL.ainvoke(prompt)
        state["token_count_input"] = state["token_count_input"] + response.response_metadata.get("token_usage").get("prompt_tokens")
        state["token_count_output"] = state["token_count_output"] + response.response_metadata.get("token_usage").get("completion_tokens")
        response_text = response.content.strip()
    return response_text

def extract_json_from_response(text: str) -> dict:
    start = text.find("{")
    if start == -1:
        logger.info("[X] No JSON object found")
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

    logger.info("[X] No complete JSON object found")
    raise ValueError("No complete JSON object found")

def calculate_cost(token_count_input:int, token_count_output:int) -> float:
    # Input rates per 1 million tokens
    input_rate = settings.INPUT_RATE_PER_M
    output_rate = settings.OUTPUT_RATE_PER_M

    # Calculate costs
    input_cost = (token_count_input / 1_000_000) * input_rate
    output_cost = (token_count_output / 1_000_000) * output_rate
    total_cost = input_cost + output_cost

    return round(total_cost, 6)