# APIs
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

# Exceptions
from src.models.exceptions import GuardingError

# Configuration
from config.settings import GROQ_API_KEY
from config.settings import PROMPT_GUARD_MODEL

# Logging
import logging
logger = logging.getLogger('uvicorn.error')

async def call_prompt_guard(user_message: str):
    """
    Guard against malicious prompts. Prompts that want to cause Jailbreak.
    """
    try:
        model = ChatGroq(temperature=0, model=PROMPT_GUARD_MODEL, api_key=GROQ_API_KEY)
        prompt = HumanMessage(content=user_message)
        completion = await model.ainvoke([prompt])
        jailbreak_probability = completion.content
        if float(jailbreak_probability) > 0.2:
            logging.info("Jailbreak detected on malicious prompt")
            raise GuardingError("Jailbreak detected on malicious prompt")

    except Exception as e:
        logging.info("Error calling llama prompt guard")
        raise GuardingError("Error calling llama prompt guard: " + str(e))