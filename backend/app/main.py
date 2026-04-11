from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.interaction_router import router as interaction_router
from app.live_runtime import LiveInterviewRuntime
from app.session_manager import SessionManager
from app.websocket_router import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.live_runtime = LiveInterviewRuntime()
    app.state.session_manager = await SessionManager.create(
        redis_url=settings.redis_url,
        ttl_seconds=settings.session_ttl_seconds,
    )
    try:
        yield
    finally:
        await app.state.session_manager.close()


app = FastAPI(title="AI Interview Backbone", lifespan=lifespan)
_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_allow_origins,
    allow_origin_regex=_settings.cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(websocket_router)
app.include_router(interaction_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
