# General
from typing import Awaitable
from colorama import Fore, Style
from time import perf_counter

# LangGraph
from src.models.state import ChatState

# Helpers
from src.nodes.intent.converter import convert_audio_to_text
from src.nodes.intent.guard import call_prompt_guard
from src.utils.prompts import build_intention_prompt
from src.utils.llm import call_llm
from src.utils.llm import extract_json_from_response

# Classes
from src.nodes.intent.validator import TextValidator, AudioValidator
from langchain_core.prompt_values import PromptValue
from typing import Awaitable

# Configution
from config.settings import MAX_TEXT_SIZE
from config.settings import MAX_AUDIO_SIZE

# Logging
import logging
logger = logging.getLogger('uvicorn.error')


async def intent_detect(state: ChatState) -> ChatState:
    # Timer
    state["start_timer_intent"] = perf_counter()

    # Validate and store message
    user_message_text = ""
    if state["user_message_format"] == "text":
        validator = TextValidator(state["user_message"], format="text", max_size=MAX_TEXT_SIZE)
        user_message_text: str = validator.validate_input()
    elif state["user_message_format"] == "audio":
        validator = AudioValidator(state["user_message"], format="audio", max_size=MAX_AUDIO_SIZE)
        user_message_audio: bytes = validator.validate_input()
        user_message_text: str = await convert_audio_to_text(user_message_audio)

    # Security on malicious prompts
    await call_prompt_guard(state, user_message_text)

    # Save message
    state["user_message_str"] = user_message_text
    logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + "[✅] 👤 USER QUESTION VALIDATED: " + Style.RESET_ALL + "it took " + Fore.YELLOW + f"{perf_counter() - state['start_timer_intent']:.4f}s ⏱. " + Style.RESET_ALL + f"Message:\n{user_message_text}")

    # # Build prompt and call llm
    # intent_prompt: PromptValue = build_intention_prompt(user_message_text)
    # response_raw: str = await call_llm(intent_prompt)
    # response_obj: object = extract_json_from_response(response_raw)
    # logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + f"[✅] 👾 INTENTION DETECTED: " + Style.RESET_ALL + "it took " + Fore.YELLOW + f"{perf_counter() - state['start_timer_intent']:.4f}s ⏱. " + Style.RESET_ALL + f"{response_obj}")

    # # Update state
    # state["intent_llm"] = response_obj["intent_llm"]
    # state["intent_score"] = response_obj["intent_score"]
    # state["required_slots"] = response_obj["required_slots"]

    # Say something
    return state