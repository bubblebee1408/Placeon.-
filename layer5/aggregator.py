import math

from layer5.models import CandidateAggregate, InterviewTurn, SkillAggregate


class AggregationError(ValueError):
    pass


class AggregationEngine:
    async def aggregate(self, turns: list[InterviewTurn]) -> CandidateAggregate:
        if not turns:
            raise AggregationError("Cannot aggregate empty interview turns")

        embedding = self._aggregate_embedding(turns)
        skills = self._aggregate_skills(turns)
        return CandidateAggregate(embedding=embedding, skills=skills)

    def _aggregate_embedding(self, turns: list[InterviewTurn]) -> list[float]:
        dims = len(turns[0].embedding)
        if dims == 0:
            raise AggregationError("Embedding cannot be empty")

        for turn in turns:
            if len(turn.embedding) != dims:
                raise AggregationError("Embedding dimensions are inconsistent across turns")

        n_turns = len(turns)
        weighted_sum = [0.0] * dims
        total_weight = 0.0

        for idx, turn in enumerate(turns):
            recency = (idx + 1) / n_turns
            weight = max(turn.confidence * recency, 1e-6)
            total_weight += weight
            for dim_idx, value in enumerate(turn.embedding):
                weighted_sum[dim_idx] += value * weight

        averaged = [value / total_weight for value in weighted_sum]
        return self._l2_normalize(averaged)

    def _aggregate_skills(self, turns: list[InterviewTurn]) -> dict[str, SkillAggregate]:
        all_skills: set[str] = set()
        for turn in turns:
            all_skills.update(turn.skills.keys())

        results: dict[str, SkillAggregate] = {}
        n_turns = len(turns)

        for skill in sorted(all_skills):
            weighted_scores = 0.0
            weight_sum = 0.0
            confidences: list[float] = []
            observed_scores: list[float] = []
            evidence_bank: list[str] = []

            for idx, turn in enumerate(turns):
                signal = turn.skills.get(skill)
                if signal is None:
                    continue

                recency = (idx + 1) / n_turns
                weight = max(signal.confidence * recency, 1e-6)
                weighted_scores += signal.score * weight
                weight_sum += weight
                confidences.append(signal.confidence)
                observed_scores.append(signal.score)
                for item in signal.evidence:
                    if item not in evidence_bank:
                        evidence_bank.append(item)

            if weight_sum == 0:
                continue

            score = weighted_scores / weight_sum
            uncertainty = self._compute_uncertainty(
                confidences,
                observed_scores,
                observed_count=len(observed_scores),
                total_turns=n_turns,
            )

            results[skill] = SkillAggregate(
                score=round(max(0.0, min(score, 1.0)), 4),
                uncertainty=round(max(0.0, min(uncertainty, 1.0)), 4),
                evidence=evidence_bank,
            )

        return results

    def _compute_uncertainty(
        self,
        confidences: list[float],
        scores: list[float],
        observed_count: int,
        total_turns: int,
    ) -> float:
        if not confidences or not scores:
            return 1.0

        avg_conf = sum(confidences) / len(confidences)
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        consistency_penalty = min(math.sqrt(variance), 1.0)

        coverage = observed_count / max(total_turns, 1)
        sparsity_penalty = (1.0 - coverage) * 0.25
        base_uncertainty = (1.0 - avg_conf) * 0.6 + consistency_penalty * 0.4 + sparsity_penalty

        if avg_conf >= 0.8 and consistency_penalty <= 0.15:
            base_uncertainty *= 0.6

        return max(0.05, min(base_uncertainty, 1.0))

    def _l2_normalize(self, vector: list[float]) -> list[float]:
        norm = math.sqrt(sum(value * value for value in vector))
        if norm <= 0:
            raise AggregationError("Cannot normalize zero vector")
        return [value / norm for value in vector]
