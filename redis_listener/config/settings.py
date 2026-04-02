# Redis
import redis
from redis import asyncio as aioredis

# Configuration
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Load variables
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # REDIS
    REDIS_HOST: str = "redis"  # Docker exposed
    REDIS_PORT: int = 6379
    REDIS_DB_MEMORY: int = 0
    REDIS_DECODE_RESPONSES: bool = True

settings = Settings()
