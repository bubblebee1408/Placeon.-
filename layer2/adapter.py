import re

from layer2.config import Layer2Config
from layer2.embedding import cosine_similarity, embed_text
from layer2.models import AdapterOutput, SkillState


class CapabilityAdapter:
    def __init__(self, config: Layer2Config | None = None) -> None:
        self._config = config or Layer2Config()
        self._state: dict[str, SkillState] = {
            skill: SkillState(
                score=self._config.base_score,
                uncertainty=self._config.base_uncertainty,
            )
            for skill in self._config.tracked_skills
        }

    async def process(self, text: str) -> AdapterOutput:
        embedding = await embed_text(text)
        confidence = self._confidence(text)
        structural = self._structural_score(text)

        updated: dict[str, SkillState] = {}
        for skill in self._config.tracked_skills:
            observed = await self._observed_skill_score(text=text, embedding=embedding, skill=skill)
            current = self._state[skill]
            next_state = self._update_skill(current=current, observed_score=observed, confidence=confidence)
            updated[skill] = next_state

        self._state = updated
        return AdapterOutput(
            skills=updated,
            embedding=embedding,
            confidence=confidence,
            structural_score=structural,
        )

    async def _observed_skill_score(self, text: str, embedding: list[float], skill: str) -> float:
        prototype = await embed_text(self._skill_prompt(skill))
        semantic = (cosine_similarity(embedding, prototype) + 1.0) / 2.0
        keyword_hits = self._keyword_hits(text, skill)
        score = (semantic * 0.65) + (keyword_hits * 0.35)
        return max(0.0, min(score, 1.0))

    def _update_skill(self, current: SkillState, observed_score: float, confidence: float) -> SkillState:
        gain = 0.25 + (0.5 * confidence)
        new_score = ((1.0 - gain) * current.score) + (gain * observed_score)

        discrepancy = abs(observed_score - current.score)
        uncertainty = current.uncertainty * (1.0 - (0.45 * confidence)) + (0.25 * discrepancy)
        uncertainty = max(self._config.uncertainty_floor, min(uncertainty, 1.0))

        return SkillState(score=round(new_score, 4), uncertainty=round(uncertainty, 4))

    def _confidence(self, text: str) -> float:
        tokens = re.findall(r"[a-zA-Z0-9_]+", text)
        length_score = min(len(tokens) / 40.0, 1.0)
        clarity_score = 1.0 if text.strip().endswith((".", "!", "?")) else 0.8
        technical_terms = len(re.findall(r"\b(cache|latency|complexity|hash|scale|queue|index)\b", text.lower()))
        keyword_score = min(technical_terms / 4.0, 1.0)
        return round(max(0.05, min((length_score * 0.5) + (clarity_score * 0.2) + (keyword_score * 0.3), 1.0)), 4)

    def _structural_score(self, text: str) -> float:
        sentences = [part for part in re.split(r"[.!?]+", text) if part.strip()]
        has_structure = 1.0 if len(sentences) >= 2 else 0.6
        has_signal_words = 1.0 if re.search(r"\b(first|then|because|trade[- ]?off|therefore)\b", text.lower()) else 0.65
        return round(min((has_structure * 0.55) + (has_signal_words * 0.45), 1.0), 4)

    def _keyword_hits(self, text: str, skill: str) -> float:
        skill_keywords = {
            "caching": ["cache", "ttl", "invalidation", "redis", "cache key"],
            "scalability": ["scale", "throughput", "shard", "partition", "latency"],
            "dsa": ["array", "hash", "tree", "graph", "complexity"],
        }
        keywords = skill_keywords.get(skill, [skill])
        text_lower = text.lower()
        hits = sum(1 for keyword in keywords if keyword in text_lower)
        return min(hits / max(len(keywords), 1), 1.0)

    def _skill_prompt(self, skill: str) -> str:
        prompts = {
            "caching": "design cache invalidation ttl consistency redis key strategy",
            "scalability": "horizontal scalability throughput partitioning bottleneck reliability",
            "dsa": "data structures algorithms complexity optimization hash tree graph",
        }
        return prompts.get(skill, skill)
