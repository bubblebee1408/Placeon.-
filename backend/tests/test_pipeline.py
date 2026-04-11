import asyncio

from backend.pipeline.context_builder import build_context
from backend.pipeline.conversation_orchestrator import generate_intro
from backend.pipeline.planner import plan_next_step
from backend.schemas.generator_schema import CandidateProfile, JobProfile


def test_case1_backend_role_focus_not_frontend_heavy() -> None:
    context = build_context(
        candidate={
            "name": "A",
            "experience_years": 2,
            "skills": ["React", "Node"],
            "projects": [],
            "education": "",
        },
        job={
            "role": "Backend Engineer",
            "level": "mid",
            "required_skills": ["API design", "databases"],
            "preferred_skills": ["caching"],
        },
    )

    assert context["interview_focus"] == "backend systems"
    assert "api design" in context["skill_gaps"]
    assert "databases" in context["skill_gaps"]


def test_planner_returns_valid_plan(monkeypatch) -> None:
    plan = asyncio.run(
        plan_next_step(
            {
                "minimal_state": {
                    "last_score": 0.83,
                    "topic": "caching",
                    "difficulty": "hard",
                },
                "candidate": {
                    "name": "A",
                    "experience_years": 2,
                    "skills": ["Node", "Caching"],
                    "projects": ["Realtime API"],
                    "education": "B.Tech",
                },
                "job": {
                    "role": "Backend Engineer",
                    "company": "PlacedOn",
                    "level": "mid",
                    "required_skills": ["caching", "api design"],
                },
                "last_question": "How do you manage cache invalidation?",
                "last_answer": "We use write-through and event-based invalidation.",
                "evaluation": {
                    "score": 0.83,
                    "confidence": 0.79,
                    "strengths": ["trade-off clarity"],
                    "weaknesses": ["none major"],
                    "missing_concepts": [],
                },
                "interview_state": {
                    "phase": "technical",
                    "history": [],
                    "covered_skills": ["api design"],
                    "current_focus": "caching",
                },
            }
        )
    )
    assert plan.action == "challenge"
    assert plan.target_skill == "caching"
    assert plan.difficulty == "hard"


def test_intro_generation_returns_conversational_opener(monkeypatch) -> None:
    def fake_call_ollama(*_args, **_kwargs):
        return json.dumps(
            {
                "intro": "Hi A, welcome. We're interviewing for the Backend Engineer role at PlacedOn. We'll start with your experience and move into technical depth. Could you briefly introduce yourself?"
            }
        )

    monkeypatch.setattr("backend.pipeline.conversation_orchestrator.call_ollama", fake_call_ollama)

    intro = asyncio.run(
        generate_intro(
            candidate=CandidateProfile(
                name="A",
                experience_years=2,
                skills=["Node"],
                projects=["API platform"],
                education="B.Tech",
            ),
            job=JobProfile(
                role="Backend Engineer",
                company="PlacedOn",
                level="mid",
                required_skills=["api design"],
                preferred_skills=["caching"],
            ),
        )
    )
    assert "Backend Engineer" in intro
    assert "introduce" in intro.lower()
