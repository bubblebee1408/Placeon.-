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
        
        # Determine attention logits based on confidence and depth (Attention Residuals inspired)
        logits = []
        for idx, turn in enumerate(turns):
            depth_factor = (idx + 1) / n_turns
            # Content-dependent logit: confidence is our primary content score, depth adds positional bias
            logit = turn.confidence + (depth_factor * 0.5)
            logits.append(logit)
            
        # Softmax over logits to get learned-style aggregation weights
        max_logit = max(logits)
        exp_logits = [math.exp(l - max_logit) for l in logits]
        sum_exp = sum(exp_logits)
        weights = [e / sum_exp for e in exp_logits]

        weighted_sum = [0.0] * dims
        for idx, turn in enumerate(turns):
            weight = weights[idx]
            for dim_idx, value in enumerate(turn.embedding):
                weighted_sum[dim_idx] += value * weight

        # Standard L2 normalize after attention-weighted sum
        return self._l2_normalize(weighted_sum)

    def _aggregate_skills(self, turns: list[InterviewTurn]) -> dict[str, SkillAggregate]:
        all_skills: set[str] = set()
        for turn in turns:
            all_skills.update(turn.skills.keys())

        results: dict[str, SkillAggregate] = {}
        n_turns = len(turns)

        for skill in sorted(all_skills):
            turns_with_skill = [(idx, t) for idx, t in enumerate(turns) if t.skills.get(skill) is not None]
            if not turns_with_skill:
                continue

            # Compute attention logits for this specific skill across depth
            logits = []
            for idx, turn in turns_with_skill:
                signal = turn.skills[skill]
                depth_factor = (idx + 1) / n_turns
                logit = signal.confidence + (depth_factor * 0.5)
                logits.append(logit)

            max_logit = max(logits)
            exp_logits = [math.exp(l - max_logit) for l in logits]
            sum_exp = sum(exp_logits)
            weights = [e / sum_exp for e in exp_logits]

            weighted_scores = 0.0
            confidences: list[float] = []
            observed_scores: list[float] = []
            evidence_bank: list[str] = []

            for arr_idx, (idx, turn) in enumerate(turns_with_skill):
                signal = turn.skills[skill]
                weight = weights[arr_idx]
                
                weighted_scores += signal.score * weight
                confidences.append(signal.confidence)
                observed_scores.append(signal.score)
                for item in signal.evidence:
                    if item not in evidence_bank:
                        evidence_bank.append(item)

            score = weighted_scores
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
