import asyncio
import json

from backend.llm.generator import generate_question


def test_generator_returns_valid_json_structure(monkeypatch) -> None:
    def fake_call_ollama(*_args, **_kwargs):
        return json.dumps(
            {
                "question": "How would you design cache invalidation for a read-heavy product catalog?",
                "skill": "caching",
                "difficulty": "hard",
                "type": "system_design",
            }
        )

    monkeypatch.setattr("backend.llm.generator.call_ollama", fake_call_ollama)

    result = asyncio.run(
        generate_question(
            plan={
                "action": "deep_dive",
                "target_skill": "caching",
                "reason": "Candidate explained basics and can handle advanced trade-offs.",
                "difficulty": "hard",
                "tone": "challenging",
            },
            context={
                "candidate": {
                    "name": "Sam",
                    "experience_years": 2,
                    "skills": ["node", "caching"],
                    "projects": ["catalog"],
                    "education": "B.Tech",
                },
                "job": {
                    "role": "Backend Engineer",
                    "company": "PlacedOn",
                    "level": "mid",
                    "required_skills": ["caching", "api design"],
                    "preferred_skills": ["distributed systems"],
                },
                "last_question": "What is TTL?",
                "last_answer": "TTL evicts stale entries.",
                "previous_context": [{"question": "What is TTL?"}],
            },
        )
    )

    assert result.question.strip()
    assert result.skill == "caching"
    assert result.difficulty in {"easy", "medium", "hard"}
    assert result.type in {"conceptual", "system_design", "behavioral"}


def test_generator_raises_on_invalid_ollama_payload(monkeypatch) -> None:
    def invalid_call_ollama(*_args, **_kwargs):
        return "not json"

    monkeypatch.setattr("backend.llm.generator.call_ollama", invalid_call_ollama)

    try:
        asyncio.run(
            generate_question(
                plan={
                    "action": "follow_up",
                    "target_skill": "api design",
                    "reason": "Needs clarity on fundamentals.",
                    "difficulty": "easy",
                    "tone": "supportive",
                },
                context={
                    "candidate": {
                        "name": "Sam",
                        "experience_years": 1,
                        "skills": ["node"],
                        "projects": [],
                        "education": "",
                    },
                    "job": {
                        "role": "Backend Engineer",
                        "company": "PlacedOn",
                        "level": "junior",
                        "required_skills": ["api design"],
                        "preferred_skills": [],
                    },
                    "last_question": "Tell me about REST.",
                    "last_answer": "Not sure.",
                    "previous_context": [],
                },
            )
        )
        raise AssertionError("Expected ValueError for invalid JSON")
    except ValueError:
        pass
