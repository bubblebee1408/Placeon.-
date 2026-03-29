import math

from layer5.config import Layer5Config
from layer5.models import FitInput, FitResult


class FitMatcher:
    def __init__(self, config: Layer5Config | None = None) -> None:
        self._config = config or Layer5Config()

    async def predict(self, data: FitInput) -> FitResult:
        candidate = data.candidate_embedding
        role = data.role_vector

        if data.preference_vector is not None:
            role = self._blend(role, data.preference_vector)

        score = self._cosine_similarity(candidate, role)
        interpretation = self._interpret(score)

        return FitResult(fit_score=round(score, 4), interpretation=interpretation)

    def _blend(self, role: list[float], preference: list[float]) -> list[float]:
        if len(role) != len(preference):
            raise ValueError("role_vector and preference_vector dimensions must match")
        return [(role[idx] * 0.7) + (preference[idx] * 0.3) for idx in range(len(role))]

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if len(left) != len(right):
            raise ValueError("Embedding dimensions must match for similarity")
        if not left:
            raise ValueError("Embeddings must be non-empty")

        dot = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))

        if left_norm == 0 or right_norm == 0:
            raise ValueError("Cannot compare zero vectors")

        score = dot / (left_norm * right_norm)
        return max(-1.0, min(score, 1.0))

    def _interpret(self, score: float) -> str:
        if score >= self._config.high_alignment_threshold:
            return "high alignment"
        if score >= self._config.medium_alignment_threshold:
            return "medium alignment"
        return "low alignment"
