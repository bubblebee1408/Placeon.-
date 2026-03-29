from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SkillTurnSignal(BaseModel):
    score: float
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)


class InterviewTurn(BaseModel):
    turn_index: int
    confidence: float = Field(ge=0.0, le=1.0)
    embedding: list[float]
    skills: dict[str, SkillTurnSignal] = Field(default_factory=dict)


class SkillAggregate(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    uncertainty: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)


class CandidateAggregate(BaseModel):
    embedding: list[float]
    skills: dict[str, SkillAggregate] = Field(default_factory=dict)


class CandidateState(BaseModel):
    candidate_id: str
    embedding: list[float]
    skills: dict[str, SkillAggregate]
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FitInput(BaseModel):
    candidate_embedding: list[float]
    role_vector: list[float]
    preference_vector: list[float] | None = None


class FitResult(BaseModel):
    fit_score: float
    interpretation: str
    basis: str = "cosine similarity over embeddings"


class RenderInput(BaseModel):
    candidate_id: str
    skills: dict[str, SkillAggregate]


class Trait(BaseModel):
    title: str
    evidence: list[str]


class ProfileOutput(BaseModel):
    traits: list[Trait]
    summary: str
    confidence_notes: str
