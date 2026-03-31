from pydantic import BaseModel, Field


class Layer2Config(BaseModel):
    tracked_skills: list[str] = Field(default_factory=lambda: ["caching", "scalability", "dsa"])
    base_score: float = 0.5
    base_uncertainty: float = 0.8
    uncertainty_floor: float = 0.05
