from aot_layer.models import QuestionOutput, QuestionRequest
from backend.llm.generator import generate_question


class QuestionGenerator:
    async def generate(self, request: QuestionRequest) -> QuestionOutput:
        action_by_mode = {
            "new": "assess",
            "probe": "probe",
            "retry": "probe",  # Retries should probe the weak spot, not ask a generic simpler question
            "challenge": "challenge"
        }
        action = action_by_mode.get(request.mode, "probe")
        tone = "supportive" if request.mode == "retry" else "neutral"

        # Detect PM skills to set appropriate role context
        is_pm_skill = request.target_skill.startswith("pm_")
        role = "Product Manager" if is_pm_skill else "Intern"
        level = "mid" if is_pm_skill else "intern"
        experience = 3 if is_pm_skill else 2

        generated = await generate_question(
            plan={
                "action": action,
                "target_skill": request.target_skill,
                "reason": f"AoT transition mode={request.mode} for skill progression.",
                "difficulty": request.difficulty,
                "tone": tone,
            },
            context={
                "candidate": {
                    "name": "AoT Candidate",
                    "experience_years": experience,
                    "skills": [request.target_skill],
                    "projects": [],
                    "education": "",
                },
                "job": {
                    "role": role,
                    "company": "PlacedOn",
                    "level": level,
                    "required_skills": [request.target_skill],
                    "preferred_skills": [],
                },
                "last_question": request.last_question,
                "last_answer": request.last_answer,
                "minimal_state": request.minimal_state,
                "interview_state": {
                    "phase": "technical",
                    "covered_skills": [request.target_skill],
                    "current_focus": request.target_skill,
                },
                "previous_context": [{"mode": request.mode}],
                "probe_focus": request.probe_focus,
                "judge_summary": request.judge_summary,
            },
        )
        return QuestionOutput(
            question=generated.question,
            skill=generated.skill,
            difficulty=request.difficulty,
        )
