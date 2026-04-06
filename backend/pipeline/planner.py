import asyncio
from typing import Any

from backend.llm.ollama_client import call_ollama
from backend.schemas.generator_schema import PlanOutput
from backend.utils.json_utils import extract_json

_PLANNER_MODEL = "llama3"


async def plan_next_step(context: dict[str, Any]) -> PlanOutput:
    prompt = f"""
You are an expert interviewer.

Based on the candidate response and interview context:
- understand depth
- understand confidence
- understand gaps

Decide the best next step for a natural interview conversation.

Behavior guidance:
- weak answer -> simplify or follow_up
- strong answer -> deep_dive
- exhausted topic -> new_topic
- project mention worth probing -> explore_project

Use reasoning, not rigid thresholds.

Return ONLY JSON:
{{
  "action": "follow_up | deep_dive | new_topic | simplify | explore_project",
  "target_skill": "string",
  "reason": "short explanation",
  "difficulty": "easy | medium | hard",
  "tone": "supportive | neutral | challenging"
}}

Context:
{context}
"""
    output = await asyncio.to_thread(
        call_ollama,
        prompt,
        _PLANNER_MODEL,
        {
            "temperature": 0.4,
            "top_p": 0.9,
        },
    )
    payload = extract_json(output)
    return PlanOutput.model_validate(payload)
