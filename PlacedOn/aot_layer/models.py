from typing import Dict, List, Literal

from pydantic import BaseModel, Field

Direction = Literal["correct", "partial", "wrong"]
Mode = Literal["new", "probe", "retry", "challenge"]
Difficulty = Literal["easy", "medium", "hard"]


class StartInput(BaseModel):
    skill_vector: List[float]
    sigma2: List[float]
    past_attempts_per_skill: Dict[str, int] = Field(default_factory=dict)


class StartDecision(BaseModel):
    target_skill: str
    difficulty: Difficulty


class QuestionRequest(BaseModel):
    target_skill: str
    difficulty: Difficulty
    mode: Mode


class QuestionOutput(BaseModel):
    question: str
    skill: str
    difficulty: Difficulty


class JudgeResult(BaseModel):
    direction: Direction
    score: float = 0.5
    confidence: float
    evidence: List[str]
    missing: List[str]
    probe_recommended: bool
    probe_focus: List[str]
    recovery_possible: bool
    atomic_summary: str = ""


class EndDecision(BaseModel):
    action: Literal["probe", "retry", "move", "challenge"]
    next_mode: Mode
    next_skill: str


class InterviewState(BaseModel):
    skills: List[str]
    skill_vector: Dict[str, float] = Field(default_factory=dict)
    sigma2: Dict[str, float] = Field(default_factory=dict)
    atomic_knowledge: Dict[str, str] = Field(default_factory=dict)
    latest_summary: str = ""
    turn_index: int = 0
    current_skill: str
    current_difficulty: Difficulty = "medium"
    consecutive_turns: Dict[str, int] = Field(default_factory=dict)
    turns_per_skill: Dict[str, int] = Field(default_factory=dict)
    probes_per_skill: Dict[str, int] = Field(default_factory=dict)
    retries_per_skill: Dict[str, int] = Field(default_factory=dict)

    def compress_to_markov_state(self) -> dict:
        """Returns the pure Markov state (memoryless) for the current turn."""
        return {
            "skill_vector": self.skill_vector,
            "sigma2": self.sigma2,
            "atomic_knowledge": self.atomic_knowledge,
            "latest_summary": self.latest_summary,
            "current_skill": self.current_skill,
            "current_difficulty": self.current_difficulty,
        }


class TurnLog(BaseModel):
    turn: int
    skill: str
    mode: Mode
    question: str
    answer: str
    judge: JudgeResult
    controller_action: str


class OrchestrationResult(BaseModel):
    final_state: InterviewState
    logs: List[TurnLog]
