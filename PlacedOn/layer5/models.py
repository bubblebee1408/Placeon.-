from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SkillTurnSignal(BaseModel):
    score: float
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)


class AxisSignal(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    reasoning: str


class InterviewTurn(BaseModel):
    turn_index: int
    confidence: float = Field(ge=0.0, le=1.0)
    embedding: List[float]
    skills: Dict[str, SkillTurnSignal] = Field(default_factory=dict)
    axes: Dict[str, AxisSignal] = Field(default_factory=dict)


class SkillAggregate(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    uncertainty: float = Field(ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)


class AxisAggregate(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    uncertainty: float = Field(ge=0.0, le=1.0)
    reasoning_summary: List[str] = Field(default_factory=list)


class CandidateAggregate(BaseModel):
    embedding: List[float]
    skills: Dict[str, SkillAggregate] = Field(default_factory=dict)
    axes: Dict[str, AxisAggregate] = Field(default_factory=dict)


class CandidateState(BaseModel):
    candidate_id: str
    embedding: List[float]
    skills: Dict[str, SkillAggregate]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FitInput(BaseModel):
    candidate_embedding: List[float]
    role_vector: List[float]
    preference_vector: Optional[List[float]] = None


class FitResult(BaseModel):
    fit_score: float
    interpretation: str
    basis: str = "cosine similarity over embeddings"


class RenderInput(BaseModel):
    candidate_id: str
    skills: Dict[str, SkillAggregate]


class Trait(BaseModel):
    title: str
    evidence: List[str]


class ProfileOutput(BaseModel):
    traits: List[Trait]
    summary: str
    confidence_notes: str
