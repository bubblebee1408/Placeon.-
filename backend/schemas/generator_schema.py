from typing import Literal

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    name: str = Field(min_length=1)
    experience_years: float = Field(ge=0)
    skills: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    education: str = ""


class JobProfile(BaseModel):
    role: str = Field(min_length=1)
    company: str = Field(default="")
    level: Literal["intern", "junior", "mid", "senior"]
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)


class PlanOutput(BaseModel):
    action: Literal["follow_up", "deep_dive", "new_topic", "simplify", "explore_project"]
    target_skill: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    difficulty: Literal["easy", "medium", "hard"]
    tone: Literal["supportive", "neutral", "challenging"]


class GeneratorInput(BaseModel):
    candidate: CandidateProfile
    job: JobProfile
    plan: PlanOutput
    last_question: str = ""
    last_answer: str = ""
    previous_context: list[dict] = Field(default_factory=list)
    interview_state: dict = Field(default_factory=dict)


class QuestionOutput(BaseModel):
    question: str = Field(min_length=1)
    skill: str = Field(min_length=1)
    difficulty: Literal["easy", "medium", "hard"]
    type: Literal["conceptual", "system_design", "behavioral"]
