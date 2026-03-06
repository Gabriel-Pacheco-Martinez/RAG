# General 
from colorama import Fore, Style
from time import perf_counter

# LangGraph
from src.models.state import ChatState

# Classes
from langchain_core.prompt_values import PromptValue
from typing import Awaitable

# Helpers
from src.utils.prompts import build_topic_prompt
from src.utils.llm import call_llm
from src.utils.llm import extract_json_from_response

# Logging 
import logging
logger = logging.getLogger('uvicorn.error')

async def topic_detect(state: ChatState) -> ChatState:
    # Timer
    state["start_timer_topic"] = perf_counter()

    # Build prompt and call llm
    topic_prompt: PromptValue = build_topic_prompt(state)
    response_raw: str = await call_llm(topic_prompt)
    response_obj: object = extract_json_from_response(response_raw)
    logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + "[✅] 👾 TOPIC DETECTED: " + Style.RESET_ALL + "it took " + Fore.YELLOW + f"{perf_counter() - state['start_timer_topic']:.4f}s ⏱. " + Style.RESET_ALL + f"{response_obj}")

    # Update state
    state["topic_llm"] = response_obj["topic_llm"]
    state["topic_score"] = response_obj["topic_score"]
    state["topic_ambiguous"] = response_obj["topic_ambiguous"]
    state["topic_follow_up"] = response_obj["topic_follow_up"]
    state["info_source"] = "memory" if state["topic_follow_up"] else "rag"
    rewritten = response_obj.get("rewritten_query")
    if rewritten is not None:
        state["user_message_str"] = rewritten

    return state
