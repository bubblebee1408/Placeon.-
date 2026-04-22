from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SkillState(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    uncertainty: float = Field(ge=0.0, le=1.0)


class AdapterOutput(BaseModel):
    skills: Dict[str, SkillState]
    embedding: List[float]
    confidence: float = Field(ge=0.0, le=1.0)
    structural_score: float = Field(ge=0.0, le=1.0)


class CodeAnalysis(BaseModel):
    active: bool
    parse_success: bool
    time_complexity: str
    cyclomatic_complexity: int
    detail: str


class BehavioralSignals(BaseModel):
    consistency_score: float = Field(ge=0.0, le=1.0)
    drift_score: float = Field(ge=0.0, le=1.0)
    confidence_signal: float = Field(ge=0.0, le=1.0)


class Layer2Output(BaseModel):
    skills: Dict[str, SkillState]
    embedding: List[float]
    behavioral_signals: BehavioralSignals
    code_analysis: Optional[CodeAnalysis] = None


class TurnAssessment(BaseModel):
    text: str
    adapter_output: AdapterOutput
    code_analysis: Optional[CodeAnalysis] = None
