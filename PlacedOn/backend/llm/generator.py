import asyncio
import re
from typing import Any, Dict, List, Optional, Union

from backend.llm.ollama_client import call_ollama
from backend.schemas.generator_schema import GeneratorInput, PlanOutput, QuestionOutput
from backend.utils.json_utils import extract_json
from skill_taxonomy import display_skill, is_behavioral_skill

_GENERATOR_MODEL = "llama3"


def _default_question_type(action: str, skill: str) -> str:
    if skill.startswith("hr_"):
        return "hr_scenario"
    if is_behavioral_skill(skill):
        return "behavioral"
    if action == "challenge":
        return "system_design"
    if action == "help":
        return "conceptual"
    if action == "assess":
        return "conceptual"
    return "behavioral"


def _normalized_question(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9\s]", " ", value.lower())
    return re.sub(r"\s+", " ", normalized).strip()


def _is_duplicate_question(candidate: str, *previous: str) -> bool:
    normalized_candidate = _normalized_question(candidate)
    if not normalized_candidate:
        return False
    return any(normalized_candidate == _normalized_question(item) for item in previous if item)


def _looks_like_interviewer_question(text: str) -> bool:
    candidate = (text or "").strip().lower()
    if not candidate:
        return False

    # Hard reject obvious answer-like starts from candidate perspective.
    answer_like_starts = (
        "i ",
        "i'm ",
        "im ",
        "my ",
        "we ",
        "in my ",
    )
    if candidate.startswith(answer_like_starts):
        return False

    # Prefer explicit question punctuation, but also allow clear interviewer prompts.
    if "?" in candidate:
        return True

    interviewer_prompt_starts = (
        "tell me",
        "walk me",
        "can you",
        "could you",
        "how would",
        "what would",
        "why would",
        "explain",
        "describe",
    )
    return candidate.startswith(interviewer_prompt_starts)


def _fallback_prompt_variants(action: str, skill: str) -> list[str]:
    label = display_skill(skill)
    if skill.startswith("hr_"):
        prompts: dict[str, list[str]] = {
            "help": [
                f"Let's look at {label}. Has there been a situation where you faced a tricky scenario with this? What happened?",
                f"How would you act in an HR scenario specifically involving {label}?",
                f"Can you provide a simple example of how you handle {label} in your daily work?",
            ],
            "probe": [
                f"Let's dive a bit deeper into that {label} scenario. What were the hidden stakes or ethical considerations?",
                f"In that situation involving {label}, how did you balance team morale against strict policies?",
                f"Tell me more about the outcome of that {label} approach. Were there any consequences?",
            ],
            "challenge": [
                f"Suppose your approach to {label} led to a major conflict with a manager. How do you resolve it?",
                f"If you were pushed to compromise your {label} by a tight deadline, what exact steps would you take?",
                f"Defend your handling of {label} in a scenario where another team member actively resists your viewpoint.",
            ],
            "assess": [
                f"How do you generally approach situations involving {label}? Can you share your philosophy?",
                f"What are the most common challenges you see regarding {label} in a typical workplace?",
                f"Describe your framework for dealing with {label}.",
            ],
        }
        return prompts.get(action, [f"Here is a scenario about {label}. How would you handle it?"])

    if is_behavioral_skill(skill):
        prompts: dict[str, list[str]] = {
            "help": [
                f"Let's make this concrete. Tell me about a real situation where you showed {label}. What happened?",
                f"Take one example that shows {label}. What was the situation, what did you do, and what changed?",
                f"Pick a specific moment related to {label}. Walk me through it step by step.",
            ],
            "probe": [
                f"Stay with that example on {label}. How did you decide what to do, and what signals guided you?",
                f"Go one level deeper on {label}. What trade-offs or tensions did you have to manage?",
                f"Walk me through how you handled {label} in practice and what you learned afterward.",
            ],
            "challenge": [
                f"Imagine a harder version of that {label} situation with time pressure and competing stakeholders. How would you handle it?",
                f"Defend your approach to {label} when the situation becomes more ambiguous or high-stakes.",
                f"If your first attempt at {label} failed, what would you change next and why?",
            ],
            "assess": [
                f"What experiences do you have dealing with {label} in past projects?",
                f"Can you give an overview of your approach to {label}?",
                f"Why is {label} an important trait for a modern engineer?"
            ],
        }
        return prompts.get(action, [f"Tell me about a real example that shows {label}."])

    prompts: dict[str, list[str]] = {
        "help": [
            f"Let's simplify this with one concrete example. How would you approach {label} step by step?",
            f"No rush. Pick one {label} scenario and walk me through your solution in clear steps.",
            f"Let's break this down. For {label}, what is step 1, step 2, and step 3 in your approach?",
        ],
        "probe": [
            f"Let's go one level deeper on {label}. Can you explain your approach step by step?",
            f"In {label}, what trade-off guides your approach? Explain your steps clearly.",
            f"Walk me through your {label} approach from first decision to final validation.",
        ],
        "challenge": [
            f"Let's stress-test your {label} approach under realistic constraints. What are your exact steps?",
            f"Assume one part of your {label} design fails. How would you adapt, step by step?",
            f"Defend your {label} approach against reliability and trade-off constraints, step by step.",
        ],
        "assess": [
            f"What are the core differences between standard approaches and your approach to {label}?",
            f"Define {label} and explain when you would use it.",
            f"What is the primary benefit of using {label} in modern architecture?",
        ],
    }
    return prompts.get(action, [f"Let's check your knowledge on {label}. Explain your understanding."])


def _fallback_question(
    plan: PlanOutput,
    context: Optional[GeneratorInput] = None,
    mode: Optional[str] = None,
    skill: Optional[str] = None,
    difficulty: Optional[str] = None,
) -> QuestionOutput:
    mode = mode or plan.action
    skill = skill or plan.target_skill
    difficulty = difficulty or plan.difficulty

    variants = _fallback_prompt_variants(mode, skill)
    question = variants[0]

    if context is not None:
        prev_a = context.last_question
        prev_b = context.previous_question

        for variant in variants:
            if not _is_duplicate_question(variant, prev_a, prev_b):
                question = variant
                break

    return QuestionOutput(
        question=question,
        skill=skill,
        difficulty=difficulty,
        type=_default_question_type(mode, skill),
    )


async def generate_question(
    plan: Union[PlanOutput, Dict[str, Any]],
    context: Dict[str, Any],
) -> QuestionOutput:
    plan_payload = plan.dict() if isinstance(plan, PlanOutput) else plan

    parsed_context = GeneratorInput.parse_obj(
        {
            **context,
            "plan": plan_payload,
        }
    )

    mode = str(plan_payload.get("action") or parsed_context.plan.action)
    target_skill = str(plan_payload.get("target_skill") or parsed_context.plan.target_skill)
    difficulty = str(plan_payload.get("difficulty") or parsed_context.plan.difficulty)
    default_type = _default_question_type(mode, target_skill)
    
    hr_instruction = ""
    if target_skill.startswith("hr_"):
        hr_instruction = "\nMake this question a tricky HR scenario-based situation. Focus on ethical, behavioral, or interpersonal conflicts, and make the candidate think critically about trade-offs."
    
    action_instruction = ""
    if mode == "assess":
        action_instruction = "\nStart with a conceptual or direct question to assess foundational knowledge (e.g., definitions, core differences, basic use cases). Do NOT use a complex scenario for this."
    elif mode == "challenge":
        action_instruction = "\nPropose a complex, real-world scenario or a difficult edge case that tests depth, tradeoffs, and scaling."
    elif mode == "help":
        action_instruction = "\nProvide a simpler, grounded question or a specific concrete example to help the candidate demonstrate basic understanding."

    prompt = f"""
Generate one interview question in JSON.
mode: {mode}
topic: {target_skill}
difficulty: {difficulty}
last_question: {parsed_context.last_question}
last_answer: {parsed_context.last_answer}
minimal_state: {parsed_context.minimal_state}
previous_question: {parsed_context.previous_question}{hr_instruction}{action_instruction}

Keep it concise, natural, and not a duplicate. Reuse prior question pattern with small variation when useful.

Return JSON only:
{{
  "question": "string",
  "skill": "string",
  "difficulty": "easy | medium | hard",
  "type": "conceptual | system_design | behavioral | hr_scenario"
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
                "timeout_seconds": 300,
            },
        )
        payload = extract_json(output)
        result = QuestionOutput.parse_obj(payload)
        if not _looks_like_interviewer_question(result.question):
            return _fallback_question(
                parsed_context.plan,
                parsed_context,
                mode=mode,
                skill=target_skill,
                difficulty=difficulty,
            )
        if _is_duplicate_question(result.question, parsed_context.last_question, parsed_context.previous_question):
            return _fallback_question(
                parsed_context.plan,
                parsed_context,
                mode=mode,
                skill=target_skill,
                difficulty=difficulty,
            )
        return result
    except Exception:  # noqa: BLE001
        return _fallback_question(
            parsed_context.plan,
            parsed_context,
            mode=mode,
            skill=target_skill,
            difficulty=difficulty,
        )
