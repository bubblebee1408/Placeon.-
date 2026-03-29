import asyncio

from layer5.matcher import FitMatcher
from layer5.models import FitInput


def test_identical_embeddings_yield_high_similarity() -> None:
    matcher = FitMatcher()
    data = FitInput(
        candidate_embedding=[0.1, 0.2, 0.3],
        role_vector=[0.1, 0.2, 0.3],
    )

    result = asyncio.run(matcher.predict(data))
    assert result.fit_score > 0.99
    assert result.interpretation == "high alignment"


def test_different_embeddings_yield_lower_similarity() -> None:
    matcher = FitMatcher()
    data = FitInput(
        candidate_embedding=[1.0, 0.0, 0.0],
        role_vector=[0.0, 1.0, 0.0],
    )

    result = asyncio.run(matcher.predict(data))
    assert result.fit_score < 0.2
    assert result.interpretation in {"low alignment", "medium alignment"}


def test_output_not_expressed_as_exact_percent() -> None:
    matcher = FitMatcher()
    result = asyncio.run(
        matcher.predict(
            FitInput(
                candidate_embedding=[0.3, 0.3, 0.4],
                role_vector=[0.25, 0.35, 0.4],
            )
        )
    )

    assert "%" not in result.interpretation
    assert "alignment" in result.interpretation
