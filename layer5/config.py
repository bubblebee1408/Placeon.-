from pydantic import BaseModel, Field


class Layer5Config(BaseModel):
    top_traits_default: int = 3
    high_alignment_threshold: float = 0.75
    medium_alignment_threshold: float = 0.45
    min_trait_score: float = 0.55
    storage_backend: str = Field(default="in_memory_pgvector_sim")
