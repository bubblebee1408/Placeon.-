import asyncio
import time

from app.models import InterviewState
from app.session_manager import SessionManager


class InMemoryRedis:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._expires_at: dict[str, float] = {}

    async def get(self, key: str) -> str | None:
        if key in self._expires_at and self._expires_at[key] <= time.monotonic():
            self._store.pop(key, None)
            self._expires_at.pop(key, None)
            return None
        return self._store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self._store[key] = value
        if ex is not None:
            self._expires_at[key] = time.monotonic() + ex

    async def ttl(self, key: str) -> int:
        if key not in self._store:
            return -2
        if key not in self._expires_at:
            return -1

        remaining = self._expires_at[key] - time.monotonic()
        if remaining <= 0:
            self._store.pop(key, None)
            self._expires_at.pop(key, None)
            return -2
        return int(remaining)

    async def aclose(self) -> None:
        return None


def test_save_and_retrieve_state() -> None:
    redis = InMemoryRedis()
    manager = SessionManager(redis_client=redis, ttl_seconds=60)

    state = InterviewState(
        interview_id="session-a",
        turn=2,
        last_question="Q2",
        last_answer="A1",
        skill_vector=[0.5, 0.2, 0.8],
        performance={"clarity": 62.1},
        last_message_id="m-1",
    )

    asyncio.run(manager.set_state(state))
    loaded = asyncio.run(manager.get_state("session-a"))

    assert loaded is not None
    assert loaded.interview_id == "session-a"
    assert loaded.turn == 2
    assert loaded.last_message_id == "m-1"


def test_ttl_expiry_behavior() -> None:
    redis = InMemoryRedis()
    manager = SessionManager(redis_client=redis, ttl_seconds=1)

    state = InterviewState(
        interview_id="session-expire",
        turn=1,
        last_question="Q1",
        last_answer=None,
    )

    asyncio.run(manager.set_state(state))
    ttl = asyncio.run(manager.ttl("session-expire"))
    assert 0 <= ttl <= 1

    time.sleep(1.2)
    assert asyncio.run(manager.get_state("session-expire")) is None


def test_memory_fallback_also_expires_state() -> None:
    manager = SessionManager(redis_client=None, ttl_seconds=1)

    state = InterviewState(
        interview_id="memory-expire",
        turn=1,
        last_question="Q1",
        last_answer=None,
    )

    asyncio.run(manager.set_state(state))
    ttl = asyncio.run(manager.ttl("memory-expire"))
    assert 0 <= ttl <= 1

    time.sleep(1.2)
    assert asyncio.run(manager.get_state("memory-expire")) is None
    assert asyncio.run(manager.ttl("memory-expire")) == -2
