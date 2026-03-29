import asyncio

from layer5.models import RenderInput, SkillAggregate
from layer5.renderer import ProfileRenderer


def test_traits_are_linked_to_evidence() -> None:
    renderer = ProfileRenderer()
    data = RenderInput(
        candidate_id="cand-x",
        skills={
            "caching": SkillAggregate(
                score=0.81,
                uncertainty=0.22,
                evidence=["used Redis", "explained sharding"],
            )
        },
    )

    output = asyncio.run(renderer.render(data, top_n=2))
    assert len(output.traits) >= 1
    assert output.traits[0].evidence


def test_no_hallucinated_traits_when_evidence_missing() -> None:
    renderer = ProfileRenderer()
    data = RenderInput(
        candidate_id="cand-y",
        skills={
            "concurrency": SkillAggregate(score=0.82, uncertainty=0.2, evidence=[])
        },
    )

    output = asyncio.run(renderer.render(data, top_n=3))
    assert output.traits == []


def test_uncertainty_reflected_in_confidence_notes() -> None:
    renderer = ProfileRenderer()
    data = RenderInput(
        candidate_id="cand-z",
        skills={
            "api_design": SkillAggregate(
                score=0.7,
                uncertainty=0.65,
                evidence=["discussed versioning"],
            )
        },
    )

    output = asyncio.run(renderer.render(data, top_n=1))
    assert "uncertainty" in output.confidence_notes.lower() or "moderate confidence" in output.confidence_notes.lower()


def test_low_confidence_signals_reduce_trait_output() -> None:
    renderer = ProfileRenderer()
    data = RenderInput(
        candidate_id="cand-low",
        skills={
            "caching": SkillAggregate(score=0.49, uncertainty=0.7, evidence=["vague mention"])
        },
    )

    output = asyncio.run(renderer.render(data))
    assert output.traits == []
