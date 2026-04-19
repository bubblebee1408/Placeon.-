from aot_layer.config import AoTConfig
from aot_layer.decomposer import Decomposer
from aot_layer.models import EndDecision, InterviewState, JudgeResult, StartDecision


class Controller:
    def __init__(self, config: AoTConfig) -> None:
        self.config = config

    async def decide_start(self, state: InterviewState, decomposer: Decomposer) -> StartDecision:
        decomposed_skill = await decomposer.pick_skill(state)
        candidate_skill = self._rebalance_skill_if_needed(state, decomposed_skill)
        difficulty = self.difficulty_for_skill(state, candidate_skill)
        return StartDecision(target_skill=candidate_skill, difficulty=difficulty)

    async def decide_end(self, state: InterviewState, judge_result: JudgeResult) -> EndDecision:
        skill = state.current_skill
        
        # True Markov Memoryless condition: skip history counters, check if uncertainty has converged
        if state.sigma2.get(skill, 1.0) <= self.config.target_sigma2:
            next_skill = self._next_skill_balanced(state=state, avoid_skill=skill)
            return EndDecision(action="move", next_mode="new", next_skill=next_skill)
        
        # Fallback to prevent infinite loops if model keeps generating bad questions
        turns_for_skill = state.turns_per_skill.get(skill, 0)
        if turns_for_skill >= self.config.max_turns_per_skill:
            next_skill = self._next_skill_balanced(state=state, avoid_skill=skill)
            return EndDecision(action="move", next_mode="new", next_skill=next_skill)

        if (
            judge_result.direction == "partial"
            and judge_result.probe_recommended
            and state.probes_per_skill.get(skill, 0) < self.config.max_probes_per_skill
            and state.consecutive_turns.get(skill, 0) < self.config.max_consecutive_per_skill
        ):
            return EndDecision(action="probe", next_mode="probe", next_skill=skill)

        if (
            judge_result.direction == "wrong"
            and judge_result.recovery_possible
            and state.retries_per_skill.get(skill, 0) < self.config.max_retries_per_skill
            and state.consecutive_turns.get(skill, 0) < self.config.max_consecutive_per_skill
        ):
            return EndDecision(action="retry", next_mode="retry", next_skill=skill)

        next_skill = self._next_skill_balanced(state=state, avoid_skill=skill)
        return EndDecision(action="move", next_mode="new", next_skill=next_skill)

    def _difficulty_from_uncertainty(self, sigma2: float) -> str:
        if sigma2 >= 0.67:
            return "hard"
        if sigma2 >= 0.34:
            return "medium"
        return "easy"

    def difficulty_for_skill(self, state: InterviewState, skill: str) -> str:
        return self._difficulty_from_uncertainty(state.sigma2.get(skill, 0.0))

    def _rebalance_skill_if_needed(self, state: InterviewState, candidate_skill: str) -> str:
        if state.consecutive_turns.get(candidate_skill, 0) < self.config.max_consecutive_per_skill:
            return candidate_skill
        return self._next_skill_balanced(state=state, avoid_skill=candidate_skill)

    def _next_skill_balanced(self, state: InterviewState, avoid_skill: str | None = None) -> str:
        # True Markov: next skill is purely determined by the current state's uncertainty (sigma2)
        eligible_skills = [
            skill for skill in state.skills 
            if skill != avoid_skill and state.sigma2.get(skill, 1.0) > self.config.target_sigma2
        ]
        
        if not eligible_skills:
            # All skills converged or only avoid_skill is left. Default to highest uncertainty.
            eligible_skills = [skill for skill in state.skills if skill != avoid_skill]
            
        if not eligible_skills:
            return state.current_skill

        # Sort by highest uncertainty
        eligible_skills.sort(key=lambda s: state.sigma2.get(s, 1.0), reverse=True)
        return eligible_skills[0]
