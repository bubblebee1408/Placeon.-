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
                "action": "challenge",
                "target_skill": "caching",
                "reason": "Candidate explained basics and can handle advanced trade-offs.",
                "difficulty": "hard",
                "tone": "challenging",
            },
            context={
                "last_question": "What is TTL?",
                "last_answer": "TTL evicts stale entries.",
                "minimal_state": {
                    "last_score": 0.82,
                    "topic": "caching",
                    "difficulty": "hard",
                },
                "previous_question": "What is TTL?",
            },
        )
    )

    assert result.question.strip()
    assert result.skill == "caching"
    assert result.difficulty in {"easy", "medium", "hard"}
    assert result.type in {"conceptual", "system_design", "behavioral"}


def test_generator_fallback_on_invalid_ollama_payload(monkeypatch) -> None:
    def invalid_call_ollama(*_args, **_kwargs):
        return "not json"

    monkeypatch.setattr("backend.llm.generator.call_ollama", invalid_call_ollama)

    result = asyncio.run(
        generate_question(
            plan={
                "action": "help",
                "target_skill": "api design",
                "reason": "Needs clarity on fundamentals.",
                "difficulty": "easy",
                "tone": "supportive",
            },
            context={
                "last_question": "Tell me about REST.",
                "last_answer": "Not sure.",
                "minimal_state": {
                    "last_score": 0.2,
                    "topic": "api design",
                    "difficulty": "easy",
                },
                "previous_question": "Tell me about REST.",
            },
        )
    )
    assert result.question.strip()
    assert result.skill == "api design"
