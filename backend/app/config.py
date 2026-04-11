import os
from functools import lru_cache

from pydantic import BaseModel, Field


def _parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseModel):
    redis_url: str = Field(default="redis://localhost:6379/0")
    session_ttl_seconds: int = Field(default=1800)
    stream_delay_seconds: float = Field(default=0.05)
    cors_allow_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"],
    )
    cors_allow_origin_regex: str = Field(default=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$")
    initial_question: str = Field(default="Tell me about a backend system you designed recently.")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    cors_allow_origins = _parse_csv(
        os.getenv(
            "CORS_ALLOW_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173",
        )
    )
    return Settings(
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        session_ttl_seconds=int(os.getenv("SESSION_TTL_SECONDS", "1800")),
        stream_delay_seconds=float(os.getenv("STREAM_DELAY_SECONDS", "0.05")),
        cors_allow_origins=cors_allow_origins,
        cors_allow_origin_regex=os.getenv(
            "CORS_ALLOW_ORIGIN_REGEX",
            r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        ),
        initial_question=os.getenv(
            "INITIAL_QUESTION",
            "Tell me about a backend system you designed recently.",
        ),
    )
