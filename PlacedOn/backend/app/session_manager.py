from typing import Any
import time

try:
    from redis.asyncio import Redis
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal test environments
    Redis = Any

from .models import InterviewState


class SessionManager:
    def __init__(self, redis_client: Redis | None, ttl_seconds: int = 1800) -> None:
        self._redis = redis_client
        self._ttl_seconds = ttl_seconds
        self._memory: dict[str, tuple[str, float]] = {}

    @classmethod
    async def create(cls, redis_url: str, ttl_seconds: int = 1800) -> "SessionManager":
        if Redis is Any:
            return cls(redis_client=None, ttl_seconds=ttl_seconds)
        redis_client = Redis.from_url(redis_url, decode_responses=True)
        return cls(redis_client=redis_client, ttl_seconds=ttl_seconds)

    @staticmethod
    def _key(interview_id: str) -> str:
        return f"interview:{interview_id}"

    async def get_state(self, interview_id: str) -> InterviewState | None:
        key = self._key(interview_id)
        if self._redis is None:
            raw = self._memory_get(key)
        else:
            raw = await self._redis.get(key)
        if raw is None:
            return None
        return InterviewState.model_validate_json(raw)

    async def set_state(self, state: InterviewState) -> None:
        key = self._key(state.interview_id)
        if self._redis is None:
            expires_at = time.monotonic() + self._ttl_seconds
            self._memory[key] = (state.model_dump_json(), expires_at)
            return
        await self._redis.set(key, state.model_dump_json(), ex=self._ttl_seconds)

    async def update_state(self, interview_id: str, **updates: object) -> InterviewState:
        current_state = await self.get_state(interview_id)
        if current_state is None:
            current_state = InterviewState(interview_id=interview_id)

        next_state = current_state.model_copy(update=updates)
        await self.set_state(next_state)
        return next_state

    async def ttl(self, interview_id: str) -> int:
        if self._redis is None:
            key = self._key(interview_id)
            entry = self._memory.get(key)
            if entry is None:
                return -2

            _payload, expires_at = entry
            remaining = expires_at - time.monotonic()
            if remaining <= 0:
                self._memory.pop(key, None)
                return -2
            return int(remaining)
        return int(await self._redis.ttl(self._key(interview_id)))

    async def close(self) -> None:
        if self._redis is not None:
            await self._redis.aclose()

    def _memory_get(self, key: str) -> str | None:
        entry = self._memory.get(key)
        if entry is None:
            return None

        payload, expires_at = entry
        if expires_at <= time.monotonic():
            self._memory.pop(key, None)
            return None
        return payload
