from __future__ import annotations


def _normalize(values: list[str]) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for value in values:
        token = value.strip().lower()
        if token and token not in seen:
            seen.add(token)
            normalized.append(token)
    return normalized


def build_context(candidate: dict, job: dict) -> dict:
    candidate_skills = _normalize(candidate.get("skills", []))
    required_skills = _normalize(job.get("required_skills", []))
    preferred_skills = _normalize(job.get("preferred_skills", []))

    strong_areas = [skill for skill in candidate_skills if skill in required_skills or skill in preferred_skills]
    skill_gaps = [skill for skill in required_skills if skill not in candidate_skills]

    if strong_areas:
        target_skills = strong_areas[:2]
    elif required_skills:
        target_skills = required_skills[:2]
    else:
        target_skills = candidate_skills[:2] if candidate_skills else ["backend fundamentals"]

    role = str(job.get("role", "")).strip().lower()
    if "backend" in role:
        interview_focus = "backend systems"
    elif "frontend" in role:
        interview_focus = "frontend systems"
    elif "data" in role:
        interview_focus = "data systems"
    elif any(token in role for token in ("ai", "ml", "machine learning", "llm")):
        interview_focus = "ai engineering systems"
    else:
        interview_focus = "role-specific engineering"

    return {
        "target_skills": target_skills,
        "skill_gaps": skill_gaps,
        "experience_level": str(job.get("level", "mid")).strip().lower() or "mid",
        "interview_focus": interview_focus,
        "strong_areas": strong_areas,
    }
