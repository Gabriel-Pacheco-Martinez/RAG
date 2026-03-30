# General
import time
from dataclasses import dataclass

# Redis
import redis
from redis import asyncio as aioredis

# Configuration
from config.settings import settings
from config.settings import REDIS_CLIENT_VALIDATOR


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after: int  # 0 if allowed

class RateLimiter:
    def __init__(self, redis: aioredis.Redis, max_requests: int, window_seconds: int):
        self.redis = redis
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def _key(self, session_id: int) -> str:
        return f"rate_limit:session:{session_id}"

    async def is_allowed(self, session_id: int) -> RateLimitResult:
        now = time.time()
        window_start = now - self.window_seconds
        key = self._key(session_id)

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, "-inf", window_start)  # Remove old timestamps
            pipe.zcard(key)                                    # Count requests in window
            pipe.zrange(key, 0, 0, withscores=True)           # Get oldest timestamp
            pipe.zadd(key, {str(now): now})                   # Add current timestamp
            pipe.expire(key, self.window_seconds)              # Reset expiry

            results = await pipe.execute()

        count = results[1]

        if count >= self.max_requests:
            oldest = results[2]
            oldest_ts = oldest[0][1] if oldest else now
            retry_after = int(oldest_ts - window_start) + 1
            await self.redis.zrem(key, str(now))  # Undo the zadd
            return RateLimitResult(allowed=False, remaining=0, retry_after=retry_after)

        remaining = self.max_requests - count - 1
        return RateLimitResult(allowed=True, remaining=remaining, retry_after=0)

# Singleton
rate_limiter = RateLimiter(
    redis=REDIS_CLIENT_VALIDATOR,
    max_requests=settings.MAX_REQUESTS_PER_WINDOW,  # default 10 requests
    window_seconds=settings.WINDOW_SECONDS          # defualt 30 minutes
)