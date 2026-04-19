import asyncio

from aot_layer.config import AoTConfig
from aot_layer.models import StartInput
from aot_layer.orchestrator import AoTOrchestrator


async def _scripted_answers(_turn: int, _question: str, skill: str, mode: str) -> str:
    scripted = {
        ("caching", "new"): "I use ttl and cache key strategy for read scaling.",
        ("caching", "probe"): "Now I include ttl, invalidation with event updates, and cache key hygiene.",
        ("concurrency", "new"): "I do not know.",
        ("concurrency", "retry"): "Still unsure.",
        ("api_design", "new"): "I use versioning, pagination, and rate limit patterns.",
    }
    return scripted.get((skill, mode), "default answer")


def test_full_flow_transitions_probe_retry_move() -> None:
    orchestrator = AoTOrchestrator(config=AoTConfig(total_turn_limit=7, max_retries_per_skill=1))
    from skill_taxonomy import DEFAULT_AOT_SKILLS
    skills = DEFAULT_AOT_SKILLS
    start = StartInput(
        skill_vector=[0.3] * len(skills),
        sigma2=[0.95] * len(skills),
        past_attempts_per_skill={s: 0 for s in skills},
    )

    result = asyncio.run(orchestrator.run(start_input=start, answer_provider=_scripted_answers, max_turns=5))

    actions = [item.controller_action for item in result.logs]
    assert "probe" in actions
    assert "retry" in actions
    assert "move" in actions
    assert 3 <= len(result.logs) <= 5


def test_repeated_wrong_answers_force_move() -> None:
    async def always_wrong(_turn: int, _question: str, _skill: str, _mode: str) -> str:
        return "no idea"

    orchestrator = AoTOrchestrator(config=AoTConfig(max_retries_per_skill=2, total_turn_limit=6))
    from skill_taxonomy import DEFAULT_AOT_SKILLS
    skills = DEFAULT_AOT_SKILLS
    start = StartInput(
        skill_vector=[0.5] * len(skills),
        sigma2=[0.9] * len(skills),
        past_attempts_per_skill={s: 0 for s in skills},
    )

    result = asyncio.run(orchestrator.run(start_input=start, answer_provider=always_wrong, max_turns=4))
    actions = [item.controller_action for item in result.logs]

    assert actions.count("retry") <= 2
    assert "move" in actions
