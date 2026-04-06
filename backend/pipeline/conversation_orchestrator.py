import asyncio

from backend.llm.ollama_client import call_ollama
from backend.schemas.generator_schema import CandidateProfile, JobProfile
from backend.utils.json_utils import extract_json

_INTRO_MODEL = "llama3"


async def generate_intro(candidate: CandidateProfile, job: JobProfile) -> str:
    prompt = f"""
You are a human interviewer.

Write a natural interview opener that:
- greets the candidate by name
- mentions the role and company
- sets friendly expectations for the interview
- asks the candidate for a short introduction

Tone: natural, human, friendly.

Return ONLY JSON:
{{
  "intro": "string"
}}

Candidate:
{candidate.model_dump()}

Job:
{job.model_dump()}
"""
    output = await asyncio.to_thread(
        call_ollama,
        prompt,
        _INTRO_MODEL,
        {
            "temperature": 0.5,
            "top_p": 0.92,
        },
    )
    payload = extract_json(output)
    intro = str(payload.get("intro", "")).strip()
    if intro:
        return intro

    company = job.company.strip() or "the company"
    return (
        f"Hi {candidate.name}, welcome. We'll walk through your experience for the "
        f"{job.role} role at {company}, then explore a few technical topics. "
        "To start, could you give me a brief introduction about yourself?"
    )
