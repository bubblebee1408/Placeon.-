from __future__ import annotations

import asyncio
import os
import sys
from typing import Any

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.live_runtime import LiveInterviewRuntime
from app.models import InterviewState
from app.tts_service import MacTTSService, TTSServiceError

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from backend.llm.generator import generate_question
from backend.llm.judge import evaluate_answer
from backend.pipeline.context_builder import build_context
from backend.pipeline.conversation_orchestrator import generate_intro
from backend.pipeline.planner import plan_next_step
from backend.schemas.generator_schema import CandidateProfile, JobProfile

from interaction_layer.communication.websocket_manager import WebSocketManager
from interaction_layer.config import InteractionConfig
from interaction_layer.error_handling.recovery import RecoveryManager
from interaction_layer.models import AudioChunk, BackendTurnResponse, TurnPayload
from interaction_layer.monitoring.presence import PresenceMonitor
from interaction_layer.persona.persona_engine import PersonaEngine
from interaction_layer.session.session_manager import InterviewSessionManager
from interaction_layer.turn.turn_manager import TurnManager
from interaction_layer.voice.stt import MockSTT
from interaction_layer.voice.tts import MockTTS

router = APIRouter()

_config = InteractionConfig()
_ws_manager = WebSocketManager()
_session_layer = InterviewSessionManager(_config)
_turn_manager = TurnManager(_config)
_stt = MockSTT()
_tts = MockTTS(_config)
_presence = PresenceMonitor(_config)
_persona = PersonaEngine()
_recovery = RecoveryManager()
_interview_pipeline_state: dict[str, dict[str, Any]] = {}

_MAX_HISTORY_ITEMS = 6
_MAX_ASKED_ITEMS = 10


class GenerateQuestionRequest(BaseModel):
    session_id: str = "default"
    candidate: CandidateProfile
    job: JobProfile


class EvaluateAnswerRequest(BaseModel):
    session_id: str = "default"
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class TTSSpeakRequest(BaseModel):
    text: str = Field(min_length=1)
    voice: str | None = None
    rate: int = Field(default=185, ge=120, le=280)


def _append_bounded(items: list[Any], value: Any, max_items: int) -> list[Any]:
    items.append(value)
    if len(items) > max_items:
        del items[: len(items) - max_items]
    return items


def _pick_focus_skill(state: dict[str, Any], context: dict[str, Any]) -> str:
    covered = set(state.get("covered_skills", []))

    for skill in context.get("target_skills", []):
        normalized = str(skill).strip().lower()
        if normalized and normalized not in covered:
            return normalized

    gaps = context.get("skill_gaps", [])
    if gaps:
        return str(gaps[0]).strip().lower()

    current = str(state.get("current_skill", "")).strip().lower()
    if current:
        return current

    targets = context.get("target_skills", [])
    if targets:
        return str(targets[0]).strip().lower()

    focus = str(context.get("interview_focus", "")).strip().lower()
    if "ai" in focus:
        return "ai fundamentals"
    if "frontend" in focus:
        return "frontend fundamentals"
    return "backend fundamentals"


def _controller_enforce_phase(state: dict[str, Any]) -> None:
    if not state.get("intro_sent"):
        state["phase"] = "intro"
        return
    if state.get("phase") == "intro":
        state["phase"] = "technical"


def _ensure_interview_state(session_id: str, candidate: CandidateProfile, job: JobProfile) -> dict[str, Any]:
    candidate_payload = candidate.model_dump()
    job_payload = job.model_dump()
    context = build_context(candidate_payload, job_payload)

    state = _interview_pipeline_state.get(session_id)
    if state is None:
        if context.get("target_skills"):
            initial_focus = context["target_skills"][0]
        elif context.get("skill_gaps"):
            initial_focus = context["skill_gaps"][0]
        elif context.get("interview_focus") == "ai engineering systems":
            initial_focus = "ai fundamentals"
        else:
            initial_focus = "backend fundamentals"
        state = {
            "asked_questions": [],
            "covered_skills": [],
            "current_skill": str(initial_focus).strip().lower(),
            "current_focus": str(initial_focus).strip().lower(),
            "round": 1,
            "phase": "intro",
            "history": [],
            "intro_sent": False,
            "last_question": "",
            "last_answer": "",
            "last_evaluation": None,
            "last_plan": None,
            "minimal_state": {
                "last_score": 0.5,
                "topic": str(initial_focus).strip().lower(),
                "difficulty": "medium",
            },
            "candidate": candidate_payload,
            "job": job_payload,
            "context": context,
        }
        _interview_pipeline_state[session_id] = state
        return state

    state["candidate"] = candidate_payload
    state["job"] = job_payload
    state["context"] = context
    state["current_skill"] = _pick_focus_skill(state, context)
    state["current_focus"] = state["current_skill"]
    _controller_enforce_phase(state)
    return state


async def _backend_process_turn(app, payload: TurnPayload) -> BackendTurnResponse:
    session_manager = app.state.session_manager
    runtime = getattr(app.state, "live_runtime", None)
    if runtime is None:
        runtime = LiveInterviewRuntime()
        app.state.live_runtime = runtime

    state = await session_manager.get_state(payload.session_id)
    if state is None:
        state = InterviewState(interview_id=payload.session_id)
        state = await runtime.bootstrap_question(state)
        await session_manager.set_state(state)

    message_id = f"interaction-{payload.turn_index}-{len(payload.transcript)}"
    answered_state = state.model_copy(
        update={"last_answer": payload.transcript, "last_message_id": message_id}
    )

    next_state = await runtime.process_answer(
        state=answered_state,
        answer=payload.transcript,
        message_id=message_id,
    )
    await session_manager.set_state(next_state)

    return BackendTurnResponse(response_text=next_state.last_question)


async def _stream_persona_audio(session_id: str, backend_text: str):
    async for token in _persona.stream_backend_response(backend_text):
        yield {"type": "persona_token", "content": token["token"], "is_final": token["is_final"]}

    async for audio_frame in _tts.text_to_speech(backend_text, session_id=session_id):
        yield {
            "type": "audio_frame",
            "index": audio_frame.index,
            "content": audio_frame.data,
            "is_final": audio_frame.is_final,
        }


@router.post("/process-turn", response_model=BackendTurnResponse)
async def process_turn(payload: TurnPayload, request: Request) -> BackendTurnResponse:
    return await _backend_process_turn(request.app, payload)


@router.post("/generate-question")
async def generate_question_endpoint(payload: GenerateQuestionRequest) -> dict:
    state = _ensure_interview_state(payload.session_id, payload.candidate, payload.job)

    if not state.get("intro_sent"):
        intro_question = await generate_intro(payload.candidate, payload.job)
        state["intro_sent"] = True
        state["last_question"] = intro_question
        _append_bounded(state["history"], {"role": "ai", "text": intro_question}, _MAX_HISTORY_ITEMS)

        asked_entry = {
            "question": intro_question,
            "skill": "introduction",
            "difficulty": "easy",
            "type": "behavioral",
            "strategy": "intro",
            "round": state["round"],
        }
        _append_bounded(state["asked_questions"], asked_entry, _MAX_ASKED_ITEMS)
        state["round"] += 1
        _controller_enforce_phase(state)
        return {
            "question": intro_question,
            "skill": "introduction",
            "difficulty": "easy",
            "type": "behavioral",
            "strategy": "intro",
            "round": asked_entry["round"],
            "tags": ["introduction"],
        }

    minimal_state = state.get("minimal_state") or {
        "last_score": 0.5,
        "topic": state.get("current_focus") or "backend fundamentals",
        "difficulty": "medium",
    }

    plan = await plan_next_step(
        {
            "minimal_state": minimal_state,
            "candidate": payload.candidate.model_dump(),
            "job": payload.job.model_dump(),
            "interview_state": {
                "phase": state.get("phase", "technical"),
                "covered_skills": state.get("covered_skills", []),
                "current_focus": state.get("current_focus"),
            },
        }
    )

    result = await generate_question(
        plan=plan,
        context={
            "last_question": state.get("last_question", ""),
            "last_answer": state.get("last_answer", ""),
            "minimal_state": minimal_state,
            "previous_question": state.get("last_question", ""),
        },
    )

    asked_entry = {
        "question": result.question,
        "skill": result.skill,
        "difficulty": result.difficulty,
        "type": result.type,
        "strategy": plan.action,
        "plan_reason": plan.reason,
        "plan_tone": plan.tone,
        "round": state["round"],
    }
    _append_bounded(state["asked_questions"], asked_entry, _MAX_ASKED_ITEMS)
    if result.skill not in state["covered_skills"]:
        state["covered_skills"].append(result.skill)
    state["last_plan"] = plan.model_dump()
    state["last_question"] = result.question
    _append_bounded(state["history"], {"role": "ai", "text": result.question}, _MAX_HISTORY_ITEMS)
    state["current_focus"] = result.skill
    state["current_skill"] = result.skill
    state["minimal_state"] = {
        "last_score": float(minimal_state.get("last_score", 0.5)),
        "topic": result.skill,
        "difficulty": result.difficulty,
    }
    _controller_enforce_phase(state)
    state["round"] += 1

    return {
        **result.model_dump(),
        "strategy": plan.action,
        "plan_reason": plan.reason,
        "tone": plan.tone,
        "round": asked_entry["round"],
        "tags": [result.skill],
    }


@router.post("/evaluate-answer")
async def evaluate_answer_endpoint(payload: EvaluateAnswerRequest) -> dict:
    result = await evaluate_answer(question=payload.question, answer=payload.answer)
    state = _interview_pipeline_state.get(payload.session_id)

    if state is not None:
        state["last_answer"] = payload.answer
        state["last_evaluation"] = result.model_dump()
        _append_bounded(state["history"], {"role": "user", "text": payload.answer}, _MAX_HISTORY_ITEMS)
        previous_topic = (state.get("minimal_state") or {}).get("topic") or state.get("current_focus")
        previous_difficulty = (state.get("minimal_state") or {}).get("difficulty") or "medium"
        state["minimal_state"] = {
            "last_score": float(result.score),
            "topic": str(previous_topic),
            "difficulty": str(previous_difficulty),
        }

        if state.get("asked_questions"):
            state["asked_questions"][-1]["score"] = result.score
            state["asked_questions"][-1]["answer"] = payload.answer
            state["asked_questions"][-1]["missing_concepts"] = result.missing_concepts

    return {
        **result.model_dump(),
        "next_strategy": None,
        "current_skill": (state or {}).get("current_skill"),
    }


@router.get("/tts/voices")
async def list_tts_voices() -> dict:
    try:
        voices = await asyncio.to_thread(MacTTSService.list_voices)
    except TTSServiceError:
        return {"voices": [], "default_voice": None}

    default_voice = MacTTSService.resolve_voice(None, voices) if voices else None
    return {"voices": voices, "default_voice": default_voice}


@router.post("/tts/speak")
async def synthesize_tts(payload: TTSSpeakRequest) -> dict:
    try:
        synthesized = await asyncio.to_thread(
            MacTTSService.synthesize,
            payload.text,
            payload.voice,
            payload.rate,
        )
    except TTSServiceError as exc:
        return {"error": str(exc)}

    return synthesized


@router.websocket("/interaction/ws/{session_id}")
async def interaction_socket(websocket: WebSocket, session_id: str) -> None:
    await _ws_manager.connect(session_id=session_id, websocket=websocket)
    await _session_layer.start_session(session_id)
    await _turn_manager.start_turn(session_id=session_id, turn_index=1)

    try:
        session_manager = websocket.app.state.session_manager
        runtime = getattr(websocket.app.state, "live_runtime", None)
        if runtime is None:
            runtime = LiveInterviewRuntime()
            websocket.app.state.live_runtime = runtime

        state = await session_manager.get_state(session_id)
        if state is None:
            state = InterviewState(interview_id=session_id)
            state = await runtime.bootstrap_question(state)
            await session_manager.set_state(state)

        await _ws_manager.send_json(
            session_id,
            {
                "type": "backend_question",
                "turn": state.turn,
                "content": state.last_question,
            },
        )

        while True:
            payload = await websocket.receive_json()

            if payload.get("type") == "audio":
                chunk = AudioChunk(
                    session_id=session_id,
                    chunk_id=int(payload.get("chunk_id", 0)),
                    content=str(payload.get("content", "")),
                    is_final=bool(payload.get("is_final", False)),
                )
                event = await _stt.speech_to_text(chunk)
                await _session_layer.touch(session_id, voice_activity=bool(event.transcript))
                await _turn_manager.ingest_event(event)

                if event.interrupted:
                    await _ws_manager.send_json(
                        session_id,
                        {"type": "stt_interrupt", "detail": "stream interrupted"},
                    )
                    continue

                if event.transcript:
                    label = "final" if event.final else "partial"
                    await _ws_manager.send_json(
                        session_id,
                        {
                            "type": f"stt_{label}",
                            "transcript": event.transcript,
                            "confidence": event.confidence,
                        },
                    )

                if event.final and event.confidence < _config.stt_min_confidence:
                    action = await _recovery.on_low_confidence()
                    await _ws_manager.send_json(session_id, {"type": "recovery", **action.model_dump()})
                    continue

                completed = await _turn_manager.detect_completion(session_id)
                if not completed:
                    continue

                backend_response = await _turn_manager.submit_to_backend(
                    session_id=session_id,
                    backend_client=lambda turn_payload: _backend_process_turn(websocket.app, turn_payload),
                )

                async for frame in _stream_persona_audio(
                    session_id=session_id,
                    backend_text=backend_response.response_text,
                ):
                    await _ws_manager.send_json(session_id, frame)

                next_session = await _session_layer.increment_turn(session_id)
                if next_session is not None:
                    await _turn_manager.start_turn(
                        session_id=session_id,
                        turn_index=next_session.turn_index + 1,
                    )

            elif payload.get("type") == "stop":
                await _turn_manager.explicit_stop(session_id)
            elif payload.get("type") == "presence":
                snapshot = await _presence.snapshot(
                    camera_active=bool(payload.get("camera_active", True)),
                    tab_focused=bool(payload.get("tab_focused", True)),
                    response_latency_ms=int(payload.get("response_latency_ms", 0)),
                )
                await _ws_manager.send_json(session_id, {"type": "presence", **snapshot.model_dump()})
            elif payload.get("type") == "silence_check":
                is_silent = await _session_layer.detect_silence(session_id)
                if is_silent:
                    action = await _recovery.on_silence()
                    await _ws_manager.send_json(session_id, {"type": "recovery", **action.model_dump()})

            timed_out = await _session_layer.track_time(session_id)
            if timed_out:
                await _ws_manager.send_json(session_id, {"type": "session_timeout"})
                break

    except WebSocketDisconnect:
        pass
    finally:
        await _session_layer.end_session(session_id)
        await _ws_manager.disconnect(session_id=session_id, websocket=websocket)
