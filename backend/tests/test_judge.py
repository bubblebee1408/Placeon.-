import asyncio
import json

from backend.llm.judge import evaluate_answer


def test_judge_returns_valid_structure(monkeypatch) -> None:
    def fake_call_ollama(*_args, **_kwargs):
        return json.dumps(
            {
                "score": 0.74,
                "confidence": 0.81,
                "strengths": ["Clear trade-off articulation"],
                "weaknesses": ["Missing failure-path detail"],
                "missing_concepts": ["cache invalidation strategy"],
            }
        )

    monkeypatch.setattr("backend.llm.judge.call_ollama", fake_call_ollama)

    result = asyncio.run(
        evaluate_answer(
            question="How would you design a resilient cache layer?",
            answer="I would use cache-aside with TTL and monitor hit ratio.",
        )
    )

    assert 0.0 <= result.score <= 1.0
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.strengths) > 0
    assert len(result.weaknesses) > 0
    assert len(result.missing_concepts) > 0


def test_judge_fallback_is_neutral(monkeypatch) -> None:
    def invalid_call_ollama(*_args, **_kwargs):
        return "not-json"

    monkeypatch.setattr("backend.llm.judge.call_ollama", invalid_call_ollama)

    result = asyncio.run(
        evaluate_answer(
            question="Explain race condition prevention.",
            answer="I am not sure.",
        )
    )

    assert result.score == 0.2
    assert result.confidence == 0.55
    assert any("parsing failed" in item.lower() for item in result.weaknesses)


def test_shallow_keyword_only_answer_is_capped(monkeypatch) -> None:
    def fake_call_ollama(*_args, **_kwargs):
        return json.dumps(
            {
                "score": 0.91,
                "confidence": 0.93,
                "strengths": ["Mentions a common tool"],
                "weaknesses": [],
                "missing_concepts": [],
            }
        )

    monkeypatch.setattr("backend.llm.judge.call_ollama", fake_call_ollama)

    result = asyncio.run(
        evaluate_answer(
            question="How would you design caching?",
            answer="Use Redis",
        )
    )

    assert result.score < 0.4
    assert result.confidence <= 0.6
    assert any(
        ("keywords" in item.lower()) or ("too short" in item.lower()) for item in result.weaknesses
    )


def test_tradeoff_rich_answer_can_be_upgraded(monkeypatch) -> None:
    def fake_call_ollama(*_args, **_kwargs):
        return json.dumps(
            {
                "score": 0.83,
                "confidence": 0.76,
                "strengths": ["Solid architectural framing"],
                "weaknesses": ["Could mention edge cases"],
                "missing_concepts": ["failure-path testing"],
            }
        )

    monkeypatch.setattr("backend.llm.judge.call_ollama", fake_call_ollama)

    result = asyncio.run(
        evaluate_answer(
            question="How would you design caching?",
            answer=(
                "I use cache-aside with TTL and invalidation hooks because stale reads can hurt correctness, "
                "but shorter TTL increases load so I tune TTL by endpoint volatility and monitor hit ratio."
            ),
        )
    )

    assert result.score >= 0.85
    assert result.confidence >= 0.8


def test_basic_band_confidence_is_clamped(monkeypatch) -> None:
    def fake_call_ollama(*_args, **_kwargs):
        return json.dumps(
            {
                "score": 0.55,
                "confidence": 0.92,
                "strengths": ["Mentions one concrete technique"],
                "weaknesses": ["Limited detail"],
                "missing_concepts": ["trade-offs"],
            }
        )

    monkeypatch.setattr("backend.llm.judge.call_ollama", fake_call_ollama)

    result = asyncio.run(
        evaluate_answer(
            question="How would you design caching?",
            answer="I use Redis with TTL for frequently read data.",
        )
    )

    assert 0.4 <= result.score < 0.7
    assert 0.5 <= result.confidence <= 0.75
