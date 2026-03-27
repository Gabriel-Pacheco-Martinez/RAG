# General
from colorama import Fore, Style
import asyncio

# PyTorch
import torch
import torch.nn.functional as F

# APIs
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

# LangGraph
from src.models.state import ChatState

# Exceptions
from src.models.exceptions import GuardingError

# Configuration
from config.enums import GUARDSource
from config.settings import settings
from config.settings import GROQ_PROMPT_GUARD_MODEL 
from config.settings import HF_PROMPT_GUARD_MODEL
from config.settings import HF_PROMPT_GUARD_TOKENIZER

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

HF_PROMPT_GUARD_MODEL.config.id2label = {
    0: "BENIGN",
    1: "MALICIOUS"
}

HF_PROMPT_GUARD_MODEL.config.label2id = {
    "BENIGN": 0,
    "MALICIOUS": 1
}

def hf_guard_inference(user_message: str):
    inputs = HF_PROMPT_GUARD_TOKENIZER(user_message, return_tensors="pt")
    with torch.no_grad():
        logits = HF_PROMPT_GUARD_MODEL(**inputs).logits
    probs = F.softmax(logits, dim=-1)
    return probs[0][HF_PROMPT_GUARD_MODEL.config.label2id["MALICIOUS"]].item()

async def call_prompt_guard(state: ChatState, user_message: str):
    """
    Guard against malicious prompts. Prompts that want to cause Jailbreak.
    """
    try:
        if settings.GUARD_SOURCE == GUARDSource.GROQ:
            logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + " ☁️🍊 GUARD SOURCE USED: " + Style.RESET_ALL + f"{settings.GUARD_SOURCE}")
            model = GROQ_PROMPT_GUARD_MODEL
            prompt = HumanMessage(content=user_message)
            completion = await model.ainvoke([prompt])
            jailbreak_probability = completion.content
            if float(jailbreak_probability) > settings.GUARD_PROBABILITY_THRESHOLD:
                logger.info("Jailbreak detected on malicious prompt")
                raise GuardingError("Jailbreak detected on malicious prompt")
            
        elif settings.GUARD_SOURCE == GUARDSource.HUGGING_FACE:
            logger.info(Fore.RED + f"{state['user_session_id']}: " + Fore.CYAN + " ☁️🤗 GUARD SOURCE USED: " + Style.RESET_ALL + f"{settings.GUARD_SOURCE}")
            malicious_prob = await asyncio.to_thread(hf_guard_inference, user_message)

            if malicious_prob > settings.GUARD_PROBABILITY_THRESHOLD:
                logger.info("Jailbreak detected on malicious prompt")
                raise GuardingError("Jailbreak detected on malicious prompt")

    except Exception as e:
        logger.info("Error calling llama prompt guard")
        raise GuardingError("Error calling llama prompt guard: " + str(e))