import asyncio
from dataclasses import dataclass

@dataclass
class RerankJob:
    pairs: list[tuple[str, str]]
    future: asyncio.Future
    loop: asyncio.AbstractEventLoop