import asyncio

from layer2.adapter import CapabilityAdapter
from layer2.behavioral import BehavioralSignalTracker


def test_stable_answers_yield_higher_consistency() -> None:
    adapter = CapabilityAdapter()
    tracker = BehavioralSignalTracker()

    history = [
        asyncio.run(adapter.process("I use cache ttl and invalidation with redis.")),
        asyncio.run(adapter.process("I use cache ttl and invalidation with redis for read traffic.")),
        asyncio.run(adapter.process("I use cache ttl and invalidation to keep reads consistent.")),
    ]

    signals = asyncio.run(tracker.track(history))
    assert signals.consistency_score > 0.6


def test_sudden_semantic_change_raises_drift() -> None:
    adapter = CapabilityAdapter()
    tracker = BehavioralSignalTracker()

    history = [
        asyncio.run(adapter.process("cache ttl invalidation redis")),
        asyncio.run(adapter.process("cache key strategy for throughput")),
        asyncio.run(adapter.process("I like cooking and football stories unrelated to backend.")),
    ]

    signals = asyncio.run(tracker.track(history))
    assert signals.drift_score > 0.2
