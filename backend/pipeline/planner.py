from typing import Any

from backend.schemas.generator_schema import PlanOutput


def _to_float(value: Any, default: float = 0.5) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _score_to_mode(score: float) -> tuple[str, str, str]:
    if score < 0.4:
        return "help", "easy", "supportive"
    if score <= 0.7:
        return "probe", "medium", "neutral"
    return "challenge", "hard", "challenging"


def _pick_target_skill(context: dict[str, Any], fallback: str) -> str:
    interview_state = context.get("interview_state") or {}
    current_focus = str(interview_state.get("current_focus") or "").strip().lower()
    if current_focus:
        return current_focus

    covered = {str(skill).strip().lower() for skill in interview_state.get("covered_skills", [])}

    candidate = context.get("candidate") or {}
    for skill in candidate.get("skills", []):
        normalized = str(skill).strip().lower()
        if normalized and normalized not in covered:
            return normalized

    job = context.get("job") or {}
    for skill in job.get("required_skills", []):
        normalized = str(skill).strip().lower()
        if normalized and normalized not in covered:
            return normalized

    return fallback


def _normalize_difficulty(value: Any, fallback: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"easy", "medium", "hard"}:
        return normalized
    return fallback


async def plan_next_step(context: dict[str, Any]) -> PlanOutput:
    minimal_state = context.get("minimal_state") or {}

    score = _to_float(
        minimal_state.get("last_score", (context.get("evaluation") or {}).get("score", 0.5)),
        default=0.5,
    )
    mode, difficulty, tone = _score_to_mode(score)

    requested_topic = str(minimal_state.get("topic") or "").strip().lower()
    target_skill = requested_topic or _pick_target_skill(context, fallback="backend fundamentals")

    return PlanOutput(
        action=mode,
        target_skill=target_skill,
        reason=f"Mode selected from score {score:.2f}",
        difficulty=_normalize_difficulty(minimal_state.get("difficulty"), difficulty),
        tone=tone,
    )
