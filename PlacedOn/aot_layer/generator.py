from aot_layer.models import QuestionOutput, QuestionRequest
from backend.llm.generator import generate_question


class QuestionGenerator:
    async def generate(self, request: QuestionRequest) -> QuestionOutput:
        action_by_mode = {
            "new": "assess",
            "probe": "probe",
            "retry": "help",
            "challenge": "challenge"
        }
        action = action_by_mode.get(request.mode, "probe")
        tone = "supportive" if request.mode == "retry" else "neutral"

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
                    "experience_years": 2,
                    "skills": [request.target_skill],
                    "projects": [],
                    "education": "",
                },
                "job": {
                    "role": "Intern",
                    "company": "PlacedOn",
                    "level": "intern",
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
            },
        )
        return QuestionOutput(
            question=generated.question,
            skill=generated.skill,
            difficulty=request.difficulty,
        )
