import asyncio

from aot_layer.config import AoTConfig
from aot_layer.models import StartInput
from aot_layer.orchestrator import AoTOrchestrator
from backend.schemas.judge_schema import JudgeOutput


async def _scripted_answers(_turn: int, _question: str, skill: str, mode: str) -> str:
    scripted = {
        ("caching", "new"): "I use ttl and cache key strategy for read scaling.",
        ("caching", "probe"): "Now I include ttl, invalidation with event updates, and cache key hygiene.",
        ("concurrency", "new"): "I do not know.",
        ("concurrency", "retry"): "Still unsure.",
        ("api_design", "new"): "I use versioning, pagination, and rate limit patterns.",
    }
    return scripted.get((skill, mode), "default answer")


def test_full_flow_transitions_probe_retry_move(monkeypatch) -> None:
    async def fake_evaluate_answer(self, skill: str, answer: str) -> 'JudgeResult':
        from aot_layer.models import JudgeResult
        if "ttl" in answer or "goroutines" in answer or "REST" in answer:
            return JudgeResult(direction="partial", confidence=0.6, evidence=[], missing=["x"], probe_recommended=True, probe_focus=["x"], recovery_possible=False)
        if "cache" in answer:
            return JudgeResult(direction="correct", confidence=0.9, evidence=[], missing=[], probe_recommended=False, probe_focus=[], recovery_possible=False)
        return JudgeResult(direction="wrong", confidence=0.4, evidence=[], missing=[], probe_recommended=False, probe_focus=[], recovery_possible=True)

    async def fake_generate(*args, **kwargs):
        from aot_layer.models import QuestionOutput
        return QuestionOutput(question="Mock question?", skill="mock", difficulty="medium")

    monkeypatch.setattr("aot_layer.judge.Judge.evaluate", fake_evaluate_answer)
    monkeypatch.setattr("aot_layer.generator.QuestionGenerator.generate", fake_generate)
    skills = ["caching", "concurrency", "api_design"]
    
    orchestrator = AoTOrchestrator(config=AoTConfig(skills=skills, total_turn_limit=7, max_retries_per_skill=1))
    start = StartInput(
        skill_vector=[0.3, 0.4, 0.8],
        sigma2=[0.95, 0.85, 0.2],
        past_attempts_per_skill={s: 0 for s in skills},
    )

    result = asyncio.run(orchestrator.run(start_input=start, answer_provider=_scripted_answers, max_turns=5))

    actions = [item.controller_action for item in result.logs]
    assert "probe" in actions
    assert "retry" in actions
    assert "move" in actions
    assert 3 <= len(result.logs) <= 5


def test_repeated_wrong_answers_force_move(monkeypatch) -> None:
    async def always_wrong(_turn: int, _question: str, _skill: str, _mode: str) -> str:
        return "no idea"

    async def fake_evaluate_answer(self, skill: str, answer: str) -> 'JudgeResult':
        from aot_layer.models import JudgeResult
        return JudgeResult(direction="wrong", confidence=0.4, evidence=[], missing=[], probe_recommended=False, probe_focus=[], recovery_possible=True)
        
    async def fake_generate(*args, **kwargs):
        from aot_layer.models import QuestionOutput
        return QuestionOutput(question="Mock question?", skill="mock", difficulty="medium")

    monkeypatch.setattr("aot_layer.judge.Judge.evaluate", fake_evaluate_answer)
    monkeypatch.setattr("aot_layer.generator.QuestionGenerator.generate", fake_generate)
    skills = ["caching", "concurrency", "api_design"]
    
    orchestrator = AoTOrchestrator(config=AoTConfig(skills=skills, max_retries_per_skill=2, total_turn_limit=6))
    start = StartInput(
        skill_vector=[0.5, 0.5, 0.5],
        sigma2=[0.9, 0.3, 0.2],
        past_attempts_per_skill={s: 0 for s in skills},
    )

    result = asyncio.run(orchestrator.run(start_input=start, answer_provider=always_wrong, max_turns=4))
    actions = [item.controller_action for item in result.logs]

    assert actions.count("retry") <= 2
    assert "move" in actions
