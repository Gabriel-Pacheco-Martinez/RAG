# General
import logging.config
import json
import asyncio
import aiohttp
from colorama import Fore, Style
from pathlib import Path

# Redis
import redis
from redis import asyncio as aioredis

# Configuration
from config.settings import settings

# Logging
config_path = Path("config/logconfig.json")
with open(config_path) as f:
    log_config = json.load(f)
logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)

async def handle_expired_session(session_id: str):
    logger.info(Fore.RED + f"{session_id}:" + Style.RESET_ALL + Fore.MAGENTA + " Session expired. Notifying client." + Style.RESET_ALL)
    
    message: str = """¡Gracias por escribirnos!

    Fue un gusto ayudarte 🙌
    Por ahora damos por finalizada la conversación.

    Si necesitas algo más, puedes volver a escribirnos en cualquier momento y con gusto te ayudaremos 💬

    ¡Que tengas un excelente día!"""


    payload = {
        "account": session_id,
        "success": False,
        "error_message": message,
        "receipt_data": None,
        "transactionCode": 1
    }

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": settings.NOTIFY_API_KEY
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(settings.NOTIFY_URL, json=payload, headers=headers) as response:
                logger.info(response)

                if response.status == 200:
                    logger.info(Fore.GREEN + f"{session_id}: Notification sent successfully." + Style.RESET_ALL)
                else:
                    body = await response.text()
                    logger.error(Fore.RED + f"{session_id}: Notification failed [{response.status}]: {body}" + Style.RESET_ALL)

    except aiohttp.ClientError as e:
        logger.error(Fore.RED + f"{session_id}: Failed to reach notification endpoint: {e}" + Style.RESET_ALL)


async def listen_for_expirations():
    channel = f"__keyevent@{settings.REDIS_DB_MEMORY}__:expired"

    while True:
        try:
            # --- CRITICAL FIX: Ping before subscribing ---
            client = aioredis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB_MEMORY,
                decode_responses=settings.REDIS_DECODE_RESPONSES,
                socket_keepalive=True,
                socket_timeout=settings.REDIS_TIMEOUT_SECONDS,
            )

            await client.ping() 
            
            async with client.pubsub() as pubsub:
                await pubsub.subscribe(channel)
                logger.info(Fore.LIGHTGREEN_EX + f"Redis listener subscribed to channel: {channel}" + Style.RESET_ALL)

                async for message in pubsub.listen():
                    if message["type"] != "message":
                        continue
                    expired_key = message["data"]
                    await handle_expired_session(expired_key)

        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            logger.warning(f"Connection to REDIS lost from listener: {e}. Retrying in 5s...")
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Unexpected error in REDIS listener: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(listen_for_expirations())