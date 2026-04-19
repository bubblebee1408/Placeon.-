import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.interaction_router import router


def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


def test_text_flow_frontend_endpoints_for_junior_ai_developer(monkeypatch) -> None:
    def fake_intro_call(*_args, **_kwargs):
        return json.dumps(
            {
                "intro": (
                    "Hi Alex, welcome to the Junior AI Developer interview at PlacedOn. "
                    "We will start with your background and then move into LLM integration and prompt design. "
                    "Could you briefly introduce yourself?"
                )
            }
        )

    def fake_generator_call(*_args, **_kwargs):
        return json.dumps(
            {
                "question": "How would you iterate on prompts when your first LLM output is inconsistent?",
                "skill": "prompt engineering",
                "difficulty": "medium",
                "type": "conceptual",
            }
        )

    def fake_judge_call(*_args, **_kwargs):
        return json.dumps(
            {
                "score": 0.72,
                "confidence": 0.76,
                "strengths": ["Uses concrete prompt iteration steps"],
                "weaknesses": ["Could mention evaluation dataset"],
                "missing_concepts": ["offline prompt regression checks"],
            }
        )

    monkeypatch.setattr("backend.pipeline.conversation_orchestrator.call_ollama", fake_intro_call)
    monkeypatch.setattr("backend.llm.generator.call_ollama", fake_generator_call)
    monkeypatch.setattr("backend.llm.judge.call_ollama", fake_judge_call)

    app = _build_test_app()
    candidate = {
        "name": "Alex",
        "experience_years": 1,
        "skills": ["python", "prompt engineering", "ml fundamentals"],
        "projects": ["retrieval qa assistant"],
        "education": "B.Tech in Computer Science",
    }
    job = {
        "role": "Junior AI Developer",
        "company": "PlacedOn",
        "level": "junior",
        "required_skills": ["python", "prompt engineering", "llm api integration"],
        "preferred_skills": ["vector databases"],
    }

    with TestClient(app) as client:
        first_question = client.post(
            "/generate-question",
            json={"session_id": "fe-text-1", "candidate": candidate, "job": job},
        )
        assert first_question.status_code == 200
        first_payload = first_question.json()
        assert "Junior AI Developer" in first_payload["question"]
        assert first_payload["strategy"] == "intro"

        evaluation = client.post(
            "/evaluate-answer",
            json={
                "session_id": "fe-text-1",
                "question": first_payload["question"],
                "answer": (
                    "I start with a structured baseline prompt using representative prompts. "
                    "For example, I add constraints to balance trade-offs and reduce variance."
                ),
            },
        )
        assert evaluation.status_code == 200
        eval_payload = evaluation.json()
        assert eval_payload["score"] >= 0.6
        assert eval_payload["current_skill"] is not None

        second_question = client.post(
            "/generate-question",
            json={"session_id": "fe-text-1", "candidate": candidate, "job": job},
        )
        assert second_question.status_code == 200
        second_payload = second_question.json()
        assert second_payload["skill"] == "prompt engineering"
        assert second_payload["strategy"] == "challenge"
        assert second_payload["round"] == 2