from layer5.config import Layer5Config
from layer5.models import ProfileOutput, RenderInput, Trait


class ProfileRenderer:
    def __init__(self, config: Layer5Config | None = None) -> None:
        self._config = config or Layer5Config()

    async def render(self, data: RenderInput, top_n: int | None = None) -> ProfileOutput:
        max_traits = top_n or self._config.top_traits_default

        ranked = sorted(
            data.skills.items(),
            key=lambda item: (item[1].score, -item[1].uncertainty),
            reverse=True,
        )

        traits: list[Trait] = []
        for skill, aggregate in ranked:
            if len(traits) >= max_traits:
                break
            if aggregate.score < self._config.min_trait_score:
                continue
            if not aggregate.evidence:
                continue

            title = self._title_for(skill=skill, score=aggregate.score)
            traits.append(Trait(title=title, evidence=aggregate.evidence[:3]))

        summary = self._summary(data.candidate_id, ranked, traits)
        confidence_notes = self._confidence_notes(ranked)

        return ProfileOutput(
            traits=traits,
            summary=summary,
            confidence_notes=confidence_notes,
        )

    def _title_for(self, skill: str, score: float) -> str:
        if score >= 0.75:
            return f"Strong signal in {skill}"
        return f"Promising signal in {skill}"

    def _summary(self, candidate_id: str, ranked: list[tuple], traits: list[Trait]) -> str:
        if not traits:
            return (
                f"Candidate {candidate_id} has limited high-confidence strengths from available evidence. "
                "Additional interview depth is recommended."
            )

        top_skills = [skill for skill, _ in ranked[: len(traits)]]
        return (
            f"Candidate {candidate_id} shows strongest evidence-aligned capability in "
            f"{', '.join(top_skills)} based on interview responses."
        )

    def _confidence_notes(self, ranked: list[tuple]) -> str:
        if not ranked:
            return "Low confidence: no skill observations were available."

        high_uncertainty = [
            skill for skill, aggregate in ranked if aggregate.uncertainty >= 0.5
        ]
        if high_uncertainty:
            return (
                "Moderate confidence: uncertainty remains elevated for "
                f"{', '.join(high_uncertainty)} due to weak or inconsistent signals."
            )

        return "Higher confidence: signals are consistent with relatively low uncertainty."
