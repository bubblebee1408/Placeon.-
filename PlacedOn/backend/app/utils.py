import asyncio
import re
from collections.abc import AsyncGenerator

from .models import InterviewState


async def stream_tokens(text: str, delay_seconds: float) -> AsyncGenerator[str, None]:
    words = text.split()
    if not words:
        return

    for index, word in enumerate(words):
        suffix = " " if index < len(words) - 1 else ""
        yield word + suffix
        await asyncio.sleep(delay_seconds)


def generate_next_question(compressed_state: str) -> str:
    weak_match = re.search(r"weakest_skill=(skill_\d+\([0-9.]+\)|none)", compressed_state)
    weak_skill = weak_match.group(1) if weak_match else "none"

    if weak_skill != "none":
        return (
            f"Let's go deeper on {weak_skill}. "
            "Walk me through a real production incident and how you resolved it."
        )

    return "Great. Let's move to your API design approach for high-throughput services."


def evolve_state_from_answer(state: InterviewState, answer: str) -> InterviewState:
    vector = state.skill_vector[:] if state.skill_vector else [0.5, 0.5, 0.5]
    if not vector:
        vector = [0.5, 0.5, 0.5]

    target_idx = state.turn % len(vector)
    boost = min(len(answer.strip()) / 400.0, 0.15)
    vector[target_idx] = min(1.0, vector[target_idx] + boost)

    weakest = min(vector)
    strongest = max(vector)
    performance = {
        "clarity": round((sum(vector) / len(vector)) * 100, 1),
        "consistency": round((strongest - weakest) * 100, 1),
    }

    return state.model_copy(update={"skill_vector": vector, "performance": performance})
