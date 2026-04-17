import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from .config import get_settings
from .live_runtime import LiveInterviewRuntime
from .models import IncomingMessage, InterviewState
from .utils import stream_tokens

router = APIRouter()


class ConnectionRegistry:
    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()

    async def connect(self, interview_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        stale_socket: WebSocket | None = None

        async with self._lock:
            stale_socket = self._connections.get(interview_id)
            self._connections[interview_id] = websocket

        if stale_socket is not None and stale_socket is not websocket:
            await stale_socket.close(code=1012, reason="Superseded by a newer connection")

    async def disconnect(self, interview_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            active = self._connections.get(interview_id)
            if active is websocket:
                self._connections.pop(interview_id, None)


connection_registry = ConnectionRegistry()


async def _send_streamed_question(websocket: WebSocket, question: str, turn: int) -> None:
    settings = getattr(websocket.app.state, "settings", get_settings())
    async for token in stream_tokens(question, settings.stream_delay_seconds):
        await websocket.send_json({"type": "question_token", "content": token, "turn": turn})

    await websocket.send_json({"type": "question", "content": question, "turn": turn})


@router.websocket("/ws/{interview_id}")
async def interview_socket(websocket: WebSocket, interview_id: str) -> None:
    session_manager = websocket.app.state.session_manager
    settings = getattr(websocket.app.state, "settings", get_settings())
    runtime = getattr(websocket.app.state, "live_runtime", None)
    if runtime is None:
        runtime = LiveInterviewRuntime()
        websocket.app.state.live_runtime = runtime

    await connection_registry.connect(interview_id=interview_id, websocket=websocket)

    try:
        state = await session_manager.get_state(interview_id)
        if state is None:
            state = InterviewState(interview_id=interview_id)
            state = await runtime.bootstrap_question(state)
            await session_manager.set_state(state)
            await _send_streamed_question(websocket, state.last_question, state.turn)
        elif not state.last_answer and state.last_question:
            await _send_streamed_question(websocket, state.last_question, state.turn)
        else:
            state = await runtime.bootstrap_question(state)
            await session_manager.set_state(state)
            await _send_streamed_question(websocket, state.last_question, state.turn)

        while True:
            payload = await websocket.receive_json()

            try:
                incoming = IncomingMessage.model_validate(payload)
            except ValidationError as exc:
                await websocket.send_json(
                    {"type": "error", "code": "invalid_payload", "detail": exc.errors()}
                )
                continue

            state = await session_manager.get_state(interview_id)
            if state is None:
                state = InterviewState(interview_id=interview_id)

            if incoming.message_id == state.last_message_id:
                await websocket.send_json(
                    {
                        "type": "duplicate",
                        "message_id": incoming.message_id,
                        "detail": "Message already processed",
                    }
                )
                continue

            answered_state = state.model_copy(
                update={
                    "last_answer": incoming.content,
                    "last_message_id": incoming.message_id,
                }
            )
            next_state = await runtime.process_answer(
                state=answered_state,
                answer=incoming.content,
                message_id=incoming.message_id,
            )

            await session_manager.set_state(next_state)
            await _send_streamed_question(websocket, next_state.last_question, next_state.turn)

    except WebSocketDisconnect:
        pass
    finally:
        await connection_registry.disconnect(interview_id=interview_id, websocket=websocket)
