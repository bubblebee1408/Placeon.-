import asyncio
import os
import sys

if __package__ in (None, ""):
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from layer2.adapter import CapabilityAdapter
from layer2.ast_evaluator import ASTEvaluator
from layer2.behavioral import BehavioralSignalTracker
from layer2.models import Layer2Output


async def run_demo() -> None:
    answers = [
        "I usually use cache keys with ttl and invalidation events to avoid stale reads.",
        "For scalability we shard by tenant and monitor throughput and latency bottlenecks.",
        "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target-n in seen:\n            return [seen[target-n], i]\n        seen[n] = i\n    return []",
        "I compare hash maps and trees, then reason about complexity trade-offs.",
    ]

    adapter = CapabilityAdapter()
    ast_evaluator = ASTEvaluator()
    behavioral = BehavioralSignalTracker()

    history = []
    for idx, answer in enumerate(answers, start=1):
        adapter_output = await adapter.process(answer)
        history.append(adapter_output)
        print(f"[Adapter] Turn {idx}: Skills updated")

        code_analysis = await ast_evaluator.analyze(answer)
        if code_analysis is not None:
            print(
                "[AST] Complexity computed "
                f"(time={code_analysis.time_complexity}, cyclomatic={code_analysis.cyclomatic_complexity})"
            )

    behavioral_signals = await behavioral.track(history)
    print(f"[Behavior] Drift: {behavioral_signals.drift_score}")
    print(f"[Behavior] Consistency: {behavioral_signals.consistency_score}")
    print(f"[Behavior] Confidence: {behavioral_signals.confidence_signal}")

    final = Layer2Output(
        skills=history[-1].skills,
        embedding=history[-1].embedding,
        behavioral_signals=behavioral_signals,
        code_analysis=await ast_evaluator.analyze(answers[-1]),
    )

    print("[Layer2] Final output ready")
    print(final.model_dump())


if __name__ == "__main__":
    asyncio.run(run_demo())
