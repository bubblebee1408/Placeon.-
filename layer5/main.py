import asyncio
import os
import sys

if __package__ in (None, ""):
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from layer5.aggregator import AggregationEngine
from layer5.matcher import FitMatcher
from layer5.models import FitInput, InterviewTurn, RenderInput, SkillTurnSignal
from layer5.renderer import ProfileRenderer
from layer5.storage import CandidateRepository


def _sample_turns() -> list[InterviewTurn]:
    return [
        InterviewTurn(
            turn_index=1,
            confidence=0.55,
            embedding=[0.20, 0.10, 0.30, 0.15],
            skills={
                "caching": SkillTurnSignal(
                    score=0.62,
                    confidence=0.55,
                    evidence=["explained ttl policy", "mentioned cache keys"],
                )
            },
        ),
        InterviewTurn(
            turn_index=2,
            confidence=0.70,
            embedding=[0.25, 0.15, 0.35, 0.20],
            skills={
                "caching": SkillTurnSignal(
                    score=0.78,
                    confidence=0.70,
                    evidence=["discussed invalidation strategy"],
                ),
                "api_design": SkillTurnSignal(
                    score=0.64,
                    confidence=0.68,
                    evidence=["covered pagination approach"],
                ),
            },
        ),
        InterviewTurn(
            turn_index=3,
            confidence=0.85,
            embedding=[0.30, 0.20, 0.42, 0.25],
            skills={
                "caching": SkillTurnSignal(
                    score=0.82,
                    confidence=0.83,
                    evidence=["used cache warming example"],
                ),
                "api_design": SkillTurnSignal(
                    score=0.72,
                    confidence=0.80,
                    evidence=["balanced rate limit with UX"],
                ),
            },
        ),
    ]


async def run_demo() -> None:
    turns = _sample_turns()

    aggregator = AggregationEngine()
    matcher = FitMatcher()
    renderer = ProfileRenderer()
    repository = CandidateRepository()

    aggregate = await aggregator.aggregate(turns)
    print("[Aggregation] Final vector computed")

    candidate = await repository.save_from_aggregate(
        candidate_id="cand-001",
        embedding=aggregate.embedding,
        skills=aggregate.skills,
        metadata={"source": "layer5-demo", "completed_turns": len(turns)},
    )

    fit = await matcher.predict(
        FitInput(
            candidate_embedding=candidate.embedding,
            role_vector=[0.31, 0.18, 0.40, 0.22],
            preference_vector=[0.29, 0.17, 0.38, 0.24],
        )
    )
    print(f"[Matcher] Fit score: {fit.fit_score} ({fit.interpretation})")

    profile = await renderer.render(
        RenderInput(candidate_id=candidate.candidate_id, skills=candidate.skills),
        top_n=3,
    )
    print("[Renderer] Generated traits with evidence")

    for trait in profile.traits:
        print(f"  - {trait.title}: {trait.evidence}")
    print(f"[Summary] {profile.summary}")
    print(f"[Confidence] {profile.confidence_notes}")


if __name__ == "__main__":
    asyncio.run(run_demo())
