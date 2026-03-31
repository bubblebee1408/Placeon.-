import asyncio

from layer2.adapter import CapabilityAdapter


def test_adapter_generates_embedding_and_skill_scores() -> None:
    adapter = CapabilityAdapter()
    output = asyncio.run(adapter.process("I use cache invalidation and ttl for Redis backed reads."))

    assert output.embedding
    assert "caching" in output.skills
    assert 0.0 <= output.skills["caching"].score <= 1.0


def test_embedding_dimension_is_not_fixed() -> None:
    adapter = CapabilityAdapter()
    short = asyncio.run(adapter.process("cache"))
    long = asyncio.run(
        adapter.process(
            "I use cache invalidation plus partitioning, throughput tuning, hash map lookups, and complexity analysis."
        )
    )

    assert len(short.embedding) != len(long.embedding)


def test_uncertainty_updates_down_with_high_confidence_signal() -> None:
    adapter = CapabilityAdapter()
    first = asyncio.run(adapter.process("basic answer"))
    second = asyncio.run(
        adapter.process(
            "First I define cache key strategy, then ttl, then invalidation through events because consistency matters."
        )
    )

    assert second.skills["caching"].uncertainty <= first.skills["caching"].uncertainty
