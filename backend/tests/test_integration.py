import asyncio
import json
import logging

from backend.llm.generator import generate_question
from backend.llm.judge import evaluate_answer
from backend.llm.ollama_client import call_ollama


def test_generate_then_evaluate_integration(monkeypatch) -> None:
    def fake_generator_call(*_args, **_kwargs):
        return json.dumps(
            {
                "question": "How do you design pagination for large APIs?",
                "skill": "api design",
                "difficulty": "medium",
                "type": "system_design",
            }
        )

    def fake_judge_call(*_args, **_kwargs):
        return json.dumps(
            {
                "score": 0.66,
                "confidence": 0.7,
                "strengths": ["Understands offsets and cursors"],
                "weaknesses": ["No consistency guarantees"],
                "missing_concepts": ["cursor invalidation"],
            }
        )

    monkeypatch.setattr("backend.llm.generator.call_ollama", fake_generator_call)
    monkeypatch.setattr("backend.llm.judge.call_ollama", fake_judge_call)

    generated = asyncio.run(
        generate_question(
            plan={
                "action": "new_topic",
                "target_skill": "api design",
                "reason": "Candidate can move from intro depth to architecture framing.",
                "difficulty": "medium",
                "tone": "neutral",
            },
            context={
                "candidate": {
                    "name": "Taylor",
                    "experience_years": 2,
                    "skills": ["node", "api design"],
                    "projects": ["billing api"],
                    "education": "B.E.",
                },
                "job": {
                    "role": "Backend Engineer",
                    "company": "PlacedOn",
                    "level": "mid",
                    "required_skills": ["api design", "databases"],
                    "preferred_skills": ["distributed systems"],
                },
                "last_question": "Tell me about a backend system you built.",
                "last_answer": "I built a billing API with queues.",
                "previous_context": [],
            },
        )
    )
    judged = asyncio.run(evaluate_answer(question=generated.question, answer="Use cursor-based pagination."))

    assert generated.question
    assert judged.score >= 0.0
    assert judged.confidence >= 0.0


def test_call_ollama_logs_requests(monkeypatch, caplog) -> None:
    class _Response:
        status_code = 200

        @staticmethod
        def json() -> dict[str, str]:
            return {"response": "{\"ok\": true}"}

    monkeypatch.setattr("backend.llm.ollama_client.requests.post", lambda *_args, **_kwargs: _Response())

    caplog.set_level(logging.INFO)
    payload = call_ollama(prompt="return json", model="llama3")

    assert "\"ok\": true" in payload
    assert "[OLLAMA] request sent" in caplog.text
    assert "[OLLAMA] response received" in caplog.text
