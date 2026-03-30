import asyncio

class UsageTracker:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    async def add(self, cost: float, input_tokens: int, output_tokens: int):
        async with self._lock:
            self.total_cost += cost
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens

    @property
    def summary(self):
        return {
            "total_cost": self.total_cost,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens
        }

# Single shared instance
usage_tracker = UsageTracker()