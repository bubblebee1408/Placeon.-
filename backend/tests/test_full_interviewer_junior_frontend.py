import json
import re
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings
from app.models import InterviewState
from app.websocket_router import router


class InMemorySessionManager:
    def __init__(self) -> None:
        self.storage: dict[str, InterviewState] = {}

    async def get_state(self, interview_id: str) -> InterviewState | None:
        return self.storage.get(interview_id)

    async def set_state(self, state: InterviewState) -> None:
        self.storage[state.interview_id] = state


def _build_test_app(manager: InMemorySessionManager) -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.state.session_manager = manager
    app.state.settings = Settings(stream_delay_seconds=0.0)
    return app


def _receive_final_question_frame(ws, max_frames: int = 400) -> dict:
    for _ in range(max_frames):
        payload = ws.receive_json()
        if payload.get("type") == "question":
            return payload
    raise AssertionError("No final question frame received")


def _extract_answer_from_prompt(prompt: str) -> str:
    match = re.search(r"Answer:\s*(.*)$", prompt, flags=re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()


def test_realtime_junior_frontend_interview_end_to_end(monkeypatch) -> None:
    question_bank = [
        "You are interviewing for Junior Frontend Engineer. Walk me through how you structure a reusable React component and keep it accessible.",
        "Follow-up: what would you probe first if two API responses race and the UI shows stale state?",
        "Nice. Your dashboard now lags after adding charts. How would you debug and improve frontend performance?",
        "Last one: for an infinite-scroll feed, how would you shape API contract choices from the frontend side?",
        "Thanks. Final check: if the user goes offline mid-request, how should the UI recover gracefully?",
    ]
    generator_counter = {"value": 0}

    @dataclass
    class _GeneratedQuestion:
        question: str
        skill: str
        difficulty: str

    async def fake_aot_generate_question(*_args, **_kwargs):
        request = _args[0] if _args else None
        difficulty = getattr(request, "difficulty", "medium") if request is not None else "medium"
        index = generator_counter["value"]
        generator_counter["value"] += 1
        if index >= len(question_bank):
            index = len(question_bank) - 1

        return _GeneratedQuestion(
            question=question_bank[index],
            skill="frontend_architecture",
            difficulty=difficulty,
        )

    def fake_judge_call(*args, **_kwargs):
        prompt = str(args[0]) if args else ""
        answer = _extract_answer_from_prompt(prompt)
        answer_lower = answer.lower()

        if "not sure" in answer_lower:
            return "not-json"

        if answer.strip() == "Use Redis.":
            return json.dumps(
                {
                    "score": 0.93,
                    "confidence": 0.95,
                    "strengths": ["Mentions a common tool"],
                    "weaknesses": [],
                    "missing_concepts": [],
                }
            )

        if "react devtools" in answer_lower:
            return json.dumps(
                {
                    "score": 0.83,
                    "confidence": 0.74,
                    "strengths": ["Clear debugging workflow", "Good practical prioritization"],
                    "weaknesses": ["Could quantify impact thresholds"],
                    "missing_concepts": ["rollout safeguards"],
                }
            )

        return json.dumps(
            {
                "score": 0.56,
                "confidence": 0.94,
                "strengths": ["Practical mitigation steps"],
                "weaknesses": ["Needs more depth"],
                "missing_concepts": ["failure-mode handling"],
            }
        )

    monkeypatch.setattr("aot_layer.generator.generate_question", fake_aot_generate_question)
    monkeypatch.setattr("backend.llm.judge.call_ollama", fake_judge_call)

    manager = InMemorySessionManager()
    app = _build_test_app(manager)

    answers = [
        (
            "I guard race conditions by tracking request ids and cancelling stale fetches so that only the latest "
            "response updates state, but I still need explicit loading and error transitions."
        ),
        (
            "I start with React DevTools profiler and browser traces, then reduce render work with memoization and "
            "virtualization. However, aggressive caching can lower latency but risk stale UI, so I combine cache key "
            "discipline with background revalidation and user-visible refresh states."
        ),
        "Use Redis.",
        "I am not sure yet, maybe increase timeout and retry manually.",
    ]

    checkpoints: list[dict] = []

    with TestClient(app) as client:
        with client.websocket_connect("/ws/jfe-e2e") as ws:
            opening = _receive_final_question_frame(ws)
            assert opening["turn"] == 1
            assert "Junior Frontend Engineer" in opening["content"]

            for idx, answer in enumerate(answers, start=1):
                state_before = manager.storage.get("jfe-e2e")
                evaluated_skill = state_before.current_skill if state_before is not None else None

                ws.send_json(
                    {
                        "type": "answer",
                        "message_id": f"msg-{idx}",
                        "content": answer,
                    }
                )

                next_question = _receive_final_question_frame(ws)
                state = manager.storage["jfe-e2e"]
                aot_state = state.candidate_snapshot.get("aot_state", {})

                checkpoints.append(
                    {
                        "turn_after_answer": state.turn,
                        "answer": answer,
                        "evaluated_skill": evaluated_skill,
                        "next_question": next_question["content"],
                        "controller_action": state.performance.get("controller_action"),
                        "mode": state.current_mode,
                        "skill": state.current_skill,
                        "trust_score": state.latest_trust_score,
                        "anomaly_flag": state.anomaly_flag,
                        "skill_confidences": aot_state.get("skill_vector", {}),
                    }
                )

    assert len(checkpoints) == 4

    # Turn 1: medium answer with overconfident raw output should clamp confidence to medium band.
    assert checkpoints[0]["controller_action"] == "probe"
    assert checkpoints[0]["mode"] == "probe"
    turn1_skill = checkpoints[0]["evaluated_skill"]
    turn1_confidence = checkpoints[0]["skill_confidences"].get(turn1_skill, 0.0)
    assert turn1_confidence <= 0.75

    # Turn 2: trade-off-rich answer should move ahead with stronger confidence.
    assert checkpoints[1]["controller_action"] == "move"
    turn2_skill = checkpoints[1]["evaluated_skill"]
    turn2_confidence = checkpoints[1]["skill_confidences"].get(turn2_skill, 0.0)
    assert turn2_confidence >= 0.7
    assert turn2_confidence > turn1_confidence

    # Turn 3: shallow keyword-only answer should be hard-capped and trigger recovery mode.
    assert checkpoints[2]["controller_action"] == "retry"
    assert checkpoints[2]["mode"] == "retry"
    turn3_skill = checkpoints[2]["evaluated_skill"]
    turn3_confidence = checkpoints[2]["skill_confidences"].get(turn3_skill, 1.0)
    assert turn3_confidence <= 0.6
    assert turn3_confidence < turn2_confidence

    # Turn 4: invalid model payload should fallback to conservative judge output.
    assert checkpoints[3]["controller_action"] in {"retry", "move"}
    turn4_skill = checkpoints[3]["evaluated_skill"]
    turn4_confidence = checkpoints[3]["skill_confidences"].get(turn4_skill, 1.0)
    assert turn4_confidence <= 0.55

    run_summary = {
        "interview_id": "jfe-e2e",
        "role": "Junior Frontend Engineer",
        "total_answers": len(answers),
        "flow": checkpoints,
        "final_state": manager.storage["jfe-e2e"].model_dump(),
    }

    assert run_summary["final_state"]["turn"] == 5
    assert run_summary["total_answers"] == 4