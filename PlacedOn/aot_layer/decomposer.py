from aot_layer.models import InterviewState


class Decomposer:
    def _is_hr_skill(self, skill: str) -> bool:
        return skill.startswith("hr_")

    async def pick_skill(self, state: InterviewState) -> str:
        # Prioritize non-HR skills to ensure HR questions come at the end
        primary_skills = [s for s in state.skills if not self._is_hr_skill(s)]
        fallback_skills = [s for s in state.skills if self._is_hr_skill(s)]
        
        target_skills = primary_skills if primary_skills else fallback_skills
        if not target_skills:
            target_skills = state.skills

        scored = [(skill, state.sigma2.get(skill, 0.0)) for skill in target_skills]
        if not scored:
            return state.skills[0]

        max_sigma = max(value for _, value in scored)
        for skill, value in scored:
            if value == max_sigma:
                return skill
        return target_skills[0]
