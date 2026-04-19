from typing import Literal

from pydantic import BaseModel, Field

Direction = Literal["correct", "partial", "wrong"]
Mode = Literal["new", "probe", "retry"]
Difficulty = Literal["easy", "medium", "hard"]


class StartInput(BaseModel):
    skill_vector: list[float]
    sigma2: list[float]
    past_attempts_per_skill: dict[str, int] = Field(default_factory=dict)


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
    confidence: float
    evidence: list[str]
    missing: list[str]
    probe_recommended: bool
    probe_focus: list[str]
    recovery_possible: bool


class EndDecision(BaseModel):
    action: Literal["probe", "retry", "move"]
    next_mode: Mode
    next_skill: str


class InterviewState(BaseModel):
    skills: list[str]
    skill_vector: dict[str, float] = Field(default_factory=dict)
    sigma2: dict[str, float] = Field(default_factory=dict)
    turn_index: int = 0
    current_skill: str
    current_difficulty: Difficulty = "medium"
    consecutive_turns: dict[str, int] = Field(default_factory=dict)
    turns_per_skill: dict[str, int] = Field(default_factory=dict)
    probes_per_skill: dict[str, int] = Field(default_factory=dict)
    retries_per_skill: dict[str, int] = Field(default_factory=dict)

    def compress_to_markov_state(self) -> dict:
        """Returns the pure Markov state (memoryless) for the current turn."""
        return {
            "skill_vector": self.skill_vector,
            "sigma2": self.sigma2,
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
    logs: list[TurnLog]
