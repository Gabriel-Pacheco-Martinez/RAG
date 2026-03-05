# General 
from colorama import Fore, Style
from time import perf_counter

# LangGraph
import re
import json
from src.models.state import ChatState

# LangChain
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Classes
from langchain_core.prompt_values import PromptValue
from typing import Awaitable

# Helpers
from src.utils.prompts import build_topic_prompt
from src.utils.llm_client import call_llm
from src.utils.llm_client import extract_json_from_response

# Logging 
import logging
logger = logging.getLogger('uvicorn.error')

async def topic_detect(state: ChatState) -> ChatState:
    # Timer
    state["start_timer_topic"] = perf_counter()

    # Build prompt and call llm
    topic_prompt: PromptValue = build_topic_prompt(state)
    response_raw: Awaitable[str] = await call_llm(topic_prompt)
    response_obj: object = extract_json_from_response(response_raw)
    logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + "[✅] 👾 TOPIC DETECTED: " + Style.RESET_ALL + "it took " + Fore.YELLOW + f"{perf_counter() - state['start_timer_topic']:.4f}s ⏱. " + Style.RESET_ALL + f"{response_obj}")

    # Update state
    state["topic"] = response_obj["topic"]
    state["topic_confidence"] = response_obj["topic_confidence"]
    state["user_message_ambiguous"] = response_obj["user_message_ambiguous"]
    state["is_follow_up"] = response_obj["is_follow_up"]
    state["rewritten_query"] = response_obj["rewritten_query"]
    if state["is_follow_up"]:
        state["info_source"] = "memory"
    else:
        state["info_source"] = "rag"
    return state
