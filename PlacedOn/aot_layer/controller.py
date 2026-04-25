from typing import Optional

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
            if not next_skill:
                return EndDecision(action="finish", next_mode="new", next_skill=skill)
            return EndDecision(action="move", next_mode="new", next_skill=next_skill)
        
        # Fallback to prevent infinite loops if model keeps generating bad questions
        turns_for_skill = state.turns_per_skill.get(skill, 0)
        if turns_for_skill >= self.config.max_turns_per_skill:
            next_skill = self._next_skill_balanced(state=state, avoid_skill=skill)
            if not next_skill:
                return EndDecision(action="finish", next_mode="new", next_skill=skill)
            return EndDecision(action="move", next_mode="new", next_skill=next_skill)

        # Escalate to a scenario-based challenge if the candidate shows solid understanding.
        # We look at the score (>= 0.7) rather than just a strict "correct" label,
        # because human answers are natural and can be marked "partial" despite being good.
        if (
            (judge_result.direction == "correct" or judge_result.score >= 0.7)
            and state.consecutive_turns.get(skill, 0) < self.config.max_consecutive_per_skill
        ):
            # Escalate difficulty/scenario if they got it right but it's not converged yet
            import random
            from skill_taxonomy import is_behavioral_skill
            
            if is_behavioral_skill(skill):
                # Behavioral skills → lean toward scenario challenges
                escalate_to = "challenge" if random.random() > 0.3 else "probe"
            else:
                # Technical skills → mix of deeper probes and scenario challenges
                escalate_to = "challenge" if random.random() > 0.4 else "probe"
                
            return EndDecision(action=escalate_to, next_mode=escalate_to, next_skill=skill)

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
        if not next_skill:
            return EndDecision(action="finish", next_mode="new", next_skill=skill)
        return EndDecision(action="move", next_mode="new", next_skill=next_skill)

    def _difficulty_from_uncertainty(self, sigma2: float, score: float, overall_avg: float) -> str:
        # High uncertainty -> new skill. If candidate is generally strong, skip easy.
        if sigma2 >= 0.8:
            if overall_avg >= 0.65:
                return "medium"
            return "easy"
            
        if score >= 0.7:
            return "hard"
        if score >= 0.4:
            return "medium"
        return "easy"

    def difficulty_for_skill(self, state: InterviewState, skill: str) -> str:
        assessed_skills = [s for s in state.skills if state.sigma2.get(s, 1.0) < 0.9]
        overall_avg = 0.5
        if assessed_skills:
            overall_avg = sum(state.skill_vector.get(s, 0.5) for s in assessed_skills) / len(assessed_skills)
            
        return self._difficulty_from_uncertainty(
            state.sigma2.get(skill, 1.0), 
            state.skill_vector.get(skill, 0.5),
            overall_avg
        )

    def _rebalance_skill_if_needed(self, state: InterviewState, candidate_skill: str) -> str:
        if state.consecutive_turns.get(candidate_skill, 0) < self.config.max_consecutive_per_skill:
            return candidate_skill
        return self._next_skill_balanced(state=state, avoid_skill=candidate_skill)

    def _is_hr_skill(self, skill: str) -> bool:
        return skill.startswith("hr_")

    def _next_skill_balanced(self, state: InterviewState, avoid_skill: Optional[str] = None) -> Optional[str]:
        # True Markov: next skill is purely determined by the current state's uncertainty (sigma2)
        eligible_skills = [
            skill for skill in state.skills 
            if skill != avoid_skill and state.sigma2.get(skill, 1.0) > self.config.target_sigma2
        ]
        
        # Partition out HR skills to run only at the end
        non_hr_eligible = [s for s in eligible_skills if not self._is_hr_skill(s)]
        hr_eligible = [s for s in eligible_skills if self._is_hr_skill(s)]
        
        if non_hr_eligible:
            eligible_skills = non_hr_eligible
        elif hr_eligible:
            eligible_skills = hr_eligible
        
        if not eligible_skills:
            # All skills converged or only avoid_skill is left.
            return None

        # Sort by highest uncertainty
        eligible_skills.sort(key=lambda s: state.sigma2.get(s, 1.0), reverse=True)
        return eligible_skills[0]
