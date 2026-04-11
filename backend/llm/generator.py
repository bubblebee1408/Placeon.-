import asyncio
from typing import Any

from backend.llm.ollama_client import call_ollama
from backend.schemas.generator_schema import GeneratorInput, PlanOutput, QuestionOutput
from backend.utils.json_utils import extract_json

_GENERATOR_MODEL = "llama3"


def _default_question_type(action: str) -> str:
    if action == "challenge":
        return "system_design"
    if action == "help":
        return "conceptual"
    return "behavioral"


def _fallback_question(plan: PlanOutput) -> QuestionOutput:
    starter = {
        "help": "Let's simplify this.",
        "probe": "Let's go one level deeper.",
        "challenge": "Let's stress-test your approach.",
    }.get(plan.action, "Let's continue.")

    return QuestionOutput(
        question=f"{starter} For {plan.target_skill}, can you explain your approach step by step?",
        skill=plan.target_skill,
        difficulty=plan.difficulty,
        type=_default_question_type(plan.action),
    )


async def generate_question(
    plan: PlanOutput | dict[str, Any],
    context: dict[str, Any],
) -> QuestionOutput:
    plan_payload = plan.model_dump() if isinstance(plan, PlanOutput) else plan

    parsed_context = GeneratorInput.model_validate(
        {
            **context,
            "plan": plan_payload,
        }
    )

    default_type = _default_question_type(parsed_context.plan.action)
    prompt = f"""
Generate one interview question in JSON.
mode: {parsed_context.plan.action}
topic: {parsed_context.plan.target_skill}
difficulty: {parsed_context.plan.difficulty}
last_question: {parsed_context.last_question}
last_answer: {parsed_context.last_answer}
minimal_state: {parsed_context.minimal_state}
previous_question: {parsed_context.previous_question}

Keep it concise, natural, and not a duplicate. Reuse prior question pattern with small variation when useful.

Return JSON only:
{{
  "question": "string",
  "skill": "string",
  "difficulty": "easy | medium | hard",
  "type": "conceptual | system_design | behavioral"
}}
Set "type" to "{default_type}" unless it clearly does not fit.
"""

    try:
        output = await asyncio.to_thread(
            call_ollama,
            prompt,
            _GENERATOR_MODEL,
            {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 96,
                "timeout_seconds": 12,
            },
        )
        payload = extract_json(output)
        return QuestionOutput.model_validate(payload)
    except Exception:  # noqa: BLE001
        return _fallback_question(parsed_context.plan)
