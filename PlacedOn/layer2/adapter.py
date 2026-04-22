from typing import Dict, List, Optional
import re

from layer2.config import Layer2Config
from layer2.embedding import cosine_similarity, embed_text
from layer2.models import AdapterOutput, SkillState
from skill_taxonomy import SKILL_KEYWORDS, SKILL_PROMPTS, signal_terms

_SIGNAL_TERMS = signal_terms()


class CapabilityAdapter:
    def __init__(self, config: Optional[Layer2Config] = None) -> None:
        self._config = config or Layer2Config()
        self._state: Dict[str, SkillState] = {
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

        updated: Dict[str, SkillState] = {}
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

    async def _observed_skill_score(self, text: str, embedding: List[float], skill: str) -> float:
        prototype = await embed_text(self._skill_prompt(skill))
        semantic = (cosine_similarity(embedding, prototype) + 1.0) / 2.0
        keyword_hits = self._keyword_hits(text, skill)
        score = (semantic * 0.65) + (keyword_hits * 0.35)
        return max(0.0, min(score, 1.0))

    def _update_skill(self, current: SkillState, observed_score: float, confidence: float) -> SkillState:
        # State: current.score (x)
        # Uncertainty: current.uncertainty (P)
        # Observation: observed_score (z)
        # Confidence: measurement quality (controls R)

        # 1. Prediction (traits are stable, but allow small drift Q)
        p_prior = current.uncertainty + self._config.process_noise_q
        x_prior = current.score

        # 2. Measurement Noise (R)
        # Higher confidence = lower R. Scale R_base by (2.0 - confidence).
        r = self._config.measurement_noise_r_base * (2.0 - confidence)

        # 3. Kalman Gain (K)
        k = p_prior / (p_prior + r)

        # 4. Update
        new_score = x_prior + k * (observed_score - x_prior)
        new_uncertainty = (1.0 - k) * p_prior

        # Clamping
        new_uncertainty = max(self._config.uncertainty_floor, min(new_uncertainty, 1.0))
        new_score = max(0.0, min(new_score, 1.0))

        return SkillState(score=round(new_score, 4), uncertainty=round(new_uncertainty, 4))

    def _confidence(self, text: str) -> float:
        lowered = text.lower()
        tokens = re.findall(r"[a-zA-Z0-9_]+", lowered)
        length_score = min(len(tokens) / 35.0, 1.0)
        clarity_score = 1.0 if text.strip().endswith((".", "!", "?")) else 0.9
        signal_hits = sum(1 for term in _SIGNAL_TERMS if term in lowered)
        keyword_score = min(signal_hits / 5.0, 1.0)
        return round(max(0.01, min((length_score * 0.4) + (clarity_score * 0.3) + (keyword_score * 0.3), 1.0)), 4)

    def _structural_score(self, text: str) -> float:
        sentences = [part for part in re.split(r"[.!?]+", text) if part.strip()]
        has_structure = 1.0 if len(sentences) >= 2 else 0.6
        has_signal_words = 1.0 if re.search(r"\b(first|then|because|trade[- ]?off|therefore)\b", text.lower()) else 0.65
        return round(min((has_structure * 0.55) + (has_signal_words * 0.45), 1.0), 4)

    def _keyword_hits(self, text: str, skill: str) -> float:
        keywords = SKILL_KEYWORDS.get(skill, [skill])
        text_lower = text.lower()
        hits = sum(1 for keyword in keywords if keyword in text_lower)
        return min(hits / max(len(keywords), 1), 1.0)

    def _skill_prompt(self, skill: str) -> str:
        return SKILL_PROMPTS.get(skill, skill)
