import asyncio
import math

from layer5.aggregator import AggregationEngine
from layer5.models import InterviewTurn, SkillTurnSignal


def _turns() -> list[InterviewTurn]:
    return [
        InterviewTurn(
            turn_index=1,
            confidence=0.4,
            embedding=[1.0, 0.0, 0.0],
            skills={
                "caching": SkillTurnSignal(
                    score=0.4,
                    confidence=0.4,
                    evidence=["mentioned ttl"],
                )
            },
        ),
        InterviewTurn(
            turn_index=2,
            confidence=0.9,
            embedding=[0.0, 1.0, 0.0],
            skills={
                "caching": SkillTurnSignal(
                    score=0.9,
                    confidence=0.9,
                    evidence=["covered invalidation", "cache key design"],
                )
            },
        ),
    ]


def test_multi_turn_aggregation_and_embedding_normalization() -> None:
    engine = AggregationEngine()
    result = asyncio.run(engine.aggregate(_turns()))

    norm = math.sqrt(sum(value * value for value in result.embedding))
    assert abs(norm - 1.0) < 1e-6
    assert "caching" in result.skills


def test_higher_confidence_and_recency_have_higher_impact() -> None:
    engine = AggregationEngine()
    result = asyncio.run(engine.aggregate(_turns()))

    score = result.skills["caching"].score
    assert score > 0.65


def test_uncertainty_drops_with_consistent_stronger_signals() -> None:
    engine = AggregationEngine()

    turns = [
        InterviewTurn(
            turn_index=1,
            confidence=0.85,
            embedding=[0.4, 0.3, 0.2],
            skills={
                "api_design": SkillTurnSignal(
                    score=0.78,
                    confidence=0.82,
                    evidence=["used versioning"],
                )
            },
        ),
        InterviewTurn(
            turn_index=2,
            confidence=0.88,
            embedding=[0.42, 0.31, 0.2],
            skills={
                "api_design": SkillTurnSignal(
                    score=0.8,
                    confidence=0.86,
                    evidence=["covered pagination"],
                )
            },
        ),
    ]

    result = asyncio.run(engine.aggregate(turns))
    assert result.skills["api_design"].uncertainty < 0.35


def test_incomplete_interview_missing_skill_data_is_supported() -> None:
    engine = AggregationEngine()
    turns = [
        InterviewTurn(turn_index=1, confidence=0.2, embedding=[0.2, 0.2, 0.2], skills={}),
        InterviewTurn(
            turn_index=2,
            confidence=0.4,
            embedding=[0.21, 0.22, 0.23],
            skills={"caching": SkillTurnSignal(score=0.45, confidence=0.3, evidence=["basic mention"])},
        ),
    ]

    result = asyncio.run(engine.aggregate(turns))
    assert "caching" in result.skills
    assert result.skills["caching"].uncertainty >= 0.5
