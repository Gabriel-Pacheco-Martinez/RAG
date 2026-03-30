# General
from typing import Awaitable
from colorama import Fore, Style
from time import perf_counter

# LangGraph
from src.models.state import ChatState

# Helpers
from src.nodes.intent.converter import convert_audio_to_text
from src.nodes.intent.guard import call_prompt_guard

# Classes
from src.nodes.intent.validator import TextValidator, AudioValidator, RateLimitValidator

# Configution
from config.settings import settings

# Logging
import logging
logger = logging.getLogger('uvicorn.error')


async def intent_detect(state: ChatState) -> ChatState:
    # Timer
    state["start_timer_intent"] = perf_counter()

    # Validate requests limit
    await RateLimitValidator(session_id=state["user_session_id"]).validate_input()

    # Validate and store message
    user_message_text = ""
    if state["user_message_format"] == "text":
        validator = TextValidator(state["user_message"], format="text", max_size=settings.MAX_TEXT_SIZE)
        user_message_text: str = validator.validate_input()
    elif state["user_message_format"] == "audio":
        validator = AudioValidator(state["user_message"], format="audio", max_size=settings.MAX_AUDIO_SIZE)
        user_message_audio: bytes = validator.validate_input()
        user_message_text: str = await convert_audio_to_text(user_message_audio)

    # Security on malicious prompts
    await call_prompt_guard(state, user_message_text)

    # Save message
    state["user_message_str"] = user_message_text
    logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + "[✅] 👤 USER QUESTION VALIDATED: " + Style.RESET_ALL + "it took " + Fore.YELLOW + f"{perf_counter() - state['start_timer_intent']:.4f}s ⏱. " + Style.RESET_ALL + f"Message:\n{user_message_text}")

    # Say something
    return state