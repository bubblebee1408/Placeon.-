import asyncio

from backend.llm.ollama_client import call_ollama
from backend.schemas.generator_schema import CandidateProfile, JobProfile
from backend.utils.json_utils import extract_json

_INTRO_MODEL = "llama3"


async def generate_intro(candidate: CandidateProfile, job: JobProfile) -> str:
    prompt = f"""
Write a short friendly interview opener.
Mention candidate name, role, company, and ask for a brief self-introduction.
Return JSON only:
{{
  "intro": "string"
}}
candidate={candidate.model_dump()}
job={job.model_dump()}
"""
    try:
        output = await asyncio.to_thread(
            call_ollama,
            prompt,
            _INTRO_MODEL,
            {
                "temperature": 0.5,
                "top_p": 0.92,
                "num_predict": 90,
                "timeout_seconds": 10,
            },
        )
        payload = extract_json(output)
        intro = str(payload.get("intro", "")).strip()
        if intro:
            return intro
    except Exception:  # noqa: BLE001
        pass

    company = job.company.strip() or "the company"
    return (
        f"Hi {candidate.name}, welcome. We'll walk through your experience for the "
        f"{job.role} role at {company}, then explore a few technical topics. "
        "To start, could you give me a brief introduction about yourself?"
    )
