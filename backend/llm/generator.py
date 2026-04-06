import asyncio
from typing import Any

from backend.llm.ollama_client import call_ollama
from backend.schemas.generator_schema import GeneratorInput, PlanOutput, QuestionOutput
from backend.utils.json_utils import extract_json

_GENERATOR_MODEL = "llama3"


def _default_question_type(action: str) -> str:
    if action == "explore_project":
        return "behavioral"
    if action == "new_topic":
        return "system_design"
    return "conceptual"


async def generate_question(
    plan: PlanOutput | dict[str, Any],
    context: dict[str, Any],
) -> QuestionOutput:
    raw_previous = context.get("previous_context", [])
    if isinstance(raw_previous, list):
        previous_context = raw_previous
    else:
        previous_context = [
            {
                "note": str(raw_previous),
            }
        ]

    plan_payload = plan.model_dump() if isinstance(plan, PlanOutput) else plan

    parsed_context = GeneratorInput.model_validate(
        {
            **context,
            "plan": plan_payload,
            "previous_context": previous_context,
        }
    )

    default_type = _default_question_type(parsed_context.plan.action)
    prompt = f"""
You are a human interviewer.

Generate ONE interview question.

Rules:
- Follow the planner decision and reason.
- Keep the conversation natural and adaptive.
- Reference the previous answer context when relevant.
- Use smooth transition phrases and avoid abrupt jumps.
- Keep focus on this skill: {parsed_context.plan.target_skill}.
- Respect this tone: {parsed_context.plan.tone}.
- Respect this desired difficulty: {parsed_context.plan.difficulty}.
- Avoid repeating prior questions.

Return ONLY JSON:
{{
  "question": "string",
  "skill": "string",
  "difficulty": "easy | medium | hard",
  "type": "conceptual | system_design | behavioral"
}}

Context:
{parsed_context.model_dump_json()}

Set "type" to "{default_type}" unless role fit is impossible.
"""
    output = await asyncio.to_thread(
        call_ollama,
        prompt,
        _GENERATOR_MODEL,
        {
            "temperature": 0.2,
            "top_p": 0.9,
        },
    )
    payload = extract_json(output)
    return QuestionOutput.model_validate(payload)
