from pydantic import BaseModel, Field

from skill_taxonomy import DEFAULT_AOT_SKILLS


class AoTConfig(BaseModel):
    skills: list[str] = Field(default_factory=lambda: list(DEFAULT_AOT_SKILLS))
    max_consecutive_per_skill: int = 2
    max_probes_per_skill: int = 2
    max_retries_per_skill: int = 2
    max_turns_per_skill: int = 4
    default_difficulty: str = "medium"
    total_turn_limit: int = 8
    target_sigma2: float = 0.20  # True Markov stopping condition
