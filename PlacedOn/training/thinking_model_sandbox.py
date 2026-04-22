"""Isolated thinking-model sandbox for AoT controller stress tests.

This module intentionally stays outside the production interview-system path.
It simulates complex candidates, scores the thinking loop with a reward
function, and increases sampling pressure on the scenarios the model handles
poorly. That gives us a reinforcement-style curriculum without coupling the
unfinished "brain" integration into the live repo flow.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

import backend.llm.generator as generator_module
import backend.llm.judge as judge_module
from aot_layer.config import AoTConfig
from aot_layer.models import OrchestrationResult, StartInput
from aot_layer.orchestrator import AoTOrchestrator

SKILLS = ["system_design", "caching", "backend", "block_10_calibration"]


@dataclass(frozen=True)
class ThinkingScenario:
    name: str
    description: str
    ground_truth: dict[str, float]
    answers: dict[tuple[str, str], str]
    expected_actions: tuple[str, ...] = ()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the isolated PlacedOn thinking-model sandbox")
    parser.add_argument("--episodes", type=int, default=16)
    parser.add_argument("--rounds", type=int, default=4)
    parser.add_argument("--max-turns", type=int, default=6)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--report-path",
        default="training/thinking_model_sandbox_report.json",
        help="Path for the sandbox report JSON",
    )
    return parser.parse_args()


def _scenarios() -> dict[str, ThinkingScenario]:
    return {
        "tradeoff_architect": ThinkingScenario(
            name="tradeoff_architect",
            description="Strong systems thinker who explains ambiguity, failure domains, and trade-offs clearly.",
            ground_truth={
                "system_design": 0.92,
                "caching": 0.84,
                "backend": 0.86,
                "block_10_calibration": 0.78,
            },
            answers={
                ("system_design", "new"): (
                    "I start by stating the SLOs, expected traffic shape, and the single biggest failure domain. "
                    "Then I separate the write path from the read path, add queue-based buffering for spikes, "
                    "and choose graceful degradation over hard failure when dependencies wobble."
                ),
                ("caching", "new"): (
                    "I use Redis with versioned cache keys, short TTLs on volatile data, and explicit invalidation on writes. "
                    "That trades some write complexity for lower stale-read risk during heavy traffic."
                ),
                ("backend", "new"): (
                    "I design the backend around idempotent handlers, retries with jitter, and structured failure telemetry. "
                    "That keeps recovery predictable when a downstream service partially fails."
                ),
                ("block_10_calibration", "new"): (
                    "Before locking the design, I call out assumptions about traffic, consistency requirements, and recovery time. "
                    "If those assumptions move, I prefer re-scoping the solution rather than pretending the first answer was complete."
                ),
            },
        ),
        "buzzword_operator": ThinkingScenario(
            name="buzzword_operator",
            description="Sounds polished but avoids mechanism and trade-off detail.",
            ground_truth={
                "system_design": 0.34,
                "caching": 0.28,
                "backend": 0.36,
                "block_10_calibration": 0.31,
            },
            answers={
                ("system_design", "new"): "I focus on scalability, innovation, and best practices for modern architecture.",
                ("system_design", "probe"): "I usually keep things highly scalable and business aligned.",
                ("caching", "new"): "Caching is important for performance and user experience, so I always keep that in mind.",
                ("backend", "new"): "I build robust backend systems with reliability, ownership, and excellent execution.",
                ("block_10_calibration", "new"): "I am confident but also flexible depending on the situation.",
            },
            expected_actions=("probe", "retry"),
        ),
        "recovering_builder": ThinkingScenario(
            name="recovering_builder",
            description="Starts vague, then improves once the model probes or retries with clearer constraints.",
            ground_truth={
                "system_design": 0.62,
                "caching": 0.58,
                "backend": 0.64,
                "block_10_calibration": 0.72,
            },
            answers={
                ("system_design", "new"): "I would probably scale it somehow and keep an eye on reliability.",
                ("system_design", "probe"): (
                    "If we are being concrete, I would identify the write bottleneck first, then split async work behind a queue "
                    "so traffic spikes do not hit the primary path directly."
                ),
                ("caching", "new"): "I would use Redis because it is fast.",
                ("caching", "retry"): (
                    "More specifically, I would use Redis with TTL plus explicit invalidation for account-critical writes, "
                    "because a cache hit is only useful if we control stale data risk."
                ),
                ("backend", "new"): "I would create APIs and make them reliable.",
                ("backend", "probe"): (
                    "I would make write endpoints idempotent, add retry budgets, and push side effects through background workers "
                    "so the main request path stays predictable."
                ),
                ("block_10_calibration", "new"): (
                    "I would first say what I do not know yet, especially traffic assumptions and consistency needs, "
                    "before choosing the architecture."
                ),
            },
            expected_actions=("probe", "retry"),
        ),
        "panic_under_ambiguity": ThinkingScenario(
            name="panic_under_ambiguity",
            description="Technically uneven candidate who weakens under open-ended ambiguity and benefits from calibration checks.",
            ground_truth={
                "system_design": 0.46,
                "caching": 0.49,
                "backend": 0.44,
                "block_10_calibration": 0.63,
            },
            answers={
                ("system_design", "new"): "I am not totally sure without traffic constraints, and I would need to ask clarifying questions first.",
                ("system_design", "probe"): (
                    "If traffic is bursty, I would protect the write path first and degrade non-critical reads before promising full consistency."
                ),
                ("caching", "new"): "I know caching matters, but I would want to validate which reads are safe to serve stale.",
                ("backend", "new"): "I would keep the API simple and add retries.",
                ("backend", "retry"): (
                    "To be more exact, I would make retries bounded and idempotent so duplicate side effects do not corrupt state."
                ),
                ("block_10_calibration", "new"): (
                    "I would explicitly state uncertainty, ask about failure tolerance, and avoid pretending I know the final architecture too early."
                ),
            },
            expected_actions=("probe",),
        ),
    }


def _extract_answer(prompt: str) -> str:
    match = re.search(r"Answer:\s*(.*)\Z", prompt, re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()


def _sandbox_judge_call(prompt: str, *_args, **_kwargs) -> str:
    answer = _extract_answer(prompt)
    signals = judge_module._analyze_answer(answer)

    score = 0.12
    if bool(signals["has_explanation"]):
        score += 0.18
    if bool(signals["has_mechanism"]):
        score += 0.26
    if bool(signals["has_tradeoff"]):
        score += 0.18
    if bool(signals["has_example"]):
        score += 0.08
    if int(signals["token_count"]) >= 18:
        score += 0.08

    if bool(signals["very_short"]):
        score -= 0.18
    if bool(signals["keyword_only"]):
        score -= 0.20
    if bool(signals["vague"]):
        score -= 0.08

    score = max(0.05, min(score, 0.95))
    confidence = max(0.25, min(0.42 + (score * 0.55), 0.95))

    payload = {
        "score": round(score, 3),
        "confidence": round(confidence, 3),
        "strengths": [
            text
            for condition, text in (
                (bool(signals["has_mechanism"]), "Explains a concrete mechanism"),
                (bool(signals["has_tradeoff"]), "Handles trade-offs"),
                (bool(signals["has_explanation"]), "Provides reasoning"),
            )
            if condition
        ][:3],
        "weaknesses": [
            text
            for condition, text in (
                (bool(signals["keyword_only"]), "Relies on buzzwords without enough mechanism"),
                (bool(signals["vague"]), "Needs more specificity"),
            )
            if condition
        ][:3],
        "missing_concepts": [
            text
            for condition, text in (
                (not bool(signals["has_tradeoff"]), "Trade-off analysis"),
                (not bool(signals["has_mechanism"]), "Concrete mechanism"),
            )
            if condition
        ][:3],
        "intent": "partial_understanding",
        "depth": "basic",
        "clarity": "okay",
        "atomic_summary": "Synthetic sandbox judgment",
    }
    return json.dumps(payload)


def _sandbox_generator_call(*_args, **_kwargs) -> str:
    return "not-json"


async def _run_episode(
    orchestrator: AoTOrchestrator,
    scenario: ThinkingScenario,
    max_turns: int,
) -> OrchestrationResult:
    async def answer_provider(_turn: int, _question: str, skill: str, mode: str) -> str:
        return scenario.answers.get(
            (skill, mode),
            scenario.answers.get((skill, "new"), "I would reason through the trade-offs step by step."),
        )

    return await orchestrator.run(
        start_input=StartInput(
            skill_vector=[0.4] * len(SKILLS),
            sigma2=[0.85] * len(SKILLS),
            past_attempts_per_skill={skill: 0 for skill in SKILLS},
        ),
        answer_provider=answer_provider,
        max_turns=max_turns,
    )


def _mean_abs_error(result: OrchestrationResult, scenario: ThinkingScenario) -> float:
    errors = [
        abs(result.final_state.skill_vector.get(skill, 0.5) - truth)
        for skill, truth in scenario.ground_truth.items()
    ]
    return mean(errors) if errors else 0.0


def _episode_reward(result: OrchestrationResult, scenario: ThinkingScenario) -> float:
    mae = _mean_abs_error(result, scenario)
    action_bonus = 0.0
    actions = {log.controller_action for log in result.logs}
    for expected in scenario.expected_actions:
        if expected in actions:
            action_bonus += 0.05

    turn_penalty = max(len(result.logs) - 4, 0) * 0.03
    reward = (1.0 - mae) + action_bonus - turn_penalty
    return max(0.0, min(round(reward, 4), 1.0))


def _normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    total = sum(weights.values()) or 1.0
    return {name: round(value / total, 6) for name, value in weights.items()}


def _update_curriculum_weights(
    current_weights: dict[str, float],
    rewards_by_scenario: dict[str, list[float]],
) -> dict[str, float]:
    updated: dict[str, float] = {}
    for name, weight in current_weights.items():
        avg_reward = mean(rewards_by_scenario.get(name, [0.5]))
        pressure = 1.0 + max(0.0, 0.75 - avg_reward)
        updated[name] = max(0.1, weight * pressure)
    return _normalize_weights(updated)


async def run_thinking_model_sandbox(
    episodes: int,
    rounds: int,
    max_turns: int,
    seed: int,
    report_path: str,
) -> dict[str, object]:
    random.seed(seed)

    original_judge_call = judge_module.call_ollama
    original_generator_call = generator_module.call_ollama
    judge_module.call_ollama = _sandbox_judge_call
    generator_module.call_ollama = _sandbox_generator_call

    try:
        catalog = _scenarios()
        weights = _normalize_weights({name: 1.0 for name in catalog})
        per_round = max(1, episodes // max(1, rounds))
        remainder = max(0, episodes - (per_round * max(1, rounds)))
        round_reports: list[dict[str, object]] = []

        for round_idx in range(1, rounds + 1):
            orchestrator = AoTOrchestrator(
                config=AoTConfig(
                    skills=SKILLS,
                    total_turn_limit=max_turns,
                    max_retries_per_skill=2,
                    max_probes_per_skill=2,
                )
            )
            round_size = per_round + (1 if round_idx <= remainder else 0)
            rewards_by_scenario: dict[str, list[float]] = defaultdict(list)
            errors_by_scenario: dict[str, list[float]] = defaultdict(list)
            action_histogram: dict[str, int] = defaultdict(int)

            for _episode_idx in range(round_size):
                scenario_name = random.choices(
                    population=list(weights.keys()),
                    weights=list(weights.values()),
                    k=1,
                )[0]
                scenario = catalog[scenario_name]
                result = await _run_episode(orchestrator, scenario, max_turns=max_turns)
                reward = _episode_reward(result, scenario)
                mae = _mean_abs_error(result, scenario)
                rewards_by_scenario[scenario_name].append(reward)
                errors_by_scenario[scenario_name].append(mae)

                for log in result.logs:
                    action_histogram[log.controller_action] += 1

            weights = _update_curriculum_weights(weights, rewards_by_scenario)
            round_reports.append(
                {
                    "round": round_idx,
                    "episodes": round_size,
                    "avg_reward": round(mean(value for values in rewards_by_scenario.values() for value in values), 4),
                    "avg_mae": round(mean(value for values in errors_by_scenario.values() for value in values), 4),
                    "weights": weights,
                    "scenario_reward": {
                        name: round(mean(values), 4) for name, values in rewards_by_scenario.items()
                    },
                    "scenario_mae": {
                        name: round(mean(values), 4) for name, values in errors_by_scenario.items()
                    },
                    "actions": dict(sorted(action_histogram.items())),
                }
            )

        weak_scenarios = sorted(
            (
                {
                    "scenario": name,
                    "avg_reward": round(mean(report["scenario_reward"][name] for report in round_reports if name in report["scenario_reward"]), 4),
                    "avg_mae": round(mean(report["scenario_mae"][name] for report in round_reports if name in report["scenario_mae"]), 4),
                }
                for name in catalog
            ),
            key=lambda item: (item["avg_reward"], -item["avg_mae"]),
        )

        report = {
            "config": {
                "episodes": episodes,
                "rounds": rounds,
                "max_turns": max_turns,
                "seed": seed,
                "skills": SKILLS,
            },
            "summary": {
                "final_avg_reward": round(round_reports[-1]["avg_reward"], 4),
                "final_avg_mae": round(round_reports[-1]["avg_mae"], 4),
                "weakest_scenarios": weak_scenarios[:3],
                "recommendation": (
                    "Keep the sandbox separate from the production brain. Use the weakest scenarios "
                    "to tune controller thresholds and prompt templates before any integration work."
                ),
            },
            "rounds": round_reports,
        }

        output = Path(report_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report
    finally:
        judge_module.call_ollama = original_judge_call
        generator_module.call_ollama = original_generator_call


def main() -> None:
    args = parse_args()
    report = asyncio.run(
        run_thinking_model_sandbox(
            episodes=args.episodes,
            rounds=args.rounds,
            max_turns=args.max_turns,
            seed=args.seed,
            report_path=args.report_path,
        )
    )
    print(json.dumps(report["summary"], indent=2))
    print(f"report: {args.report_path}")


if __name__ == "__main__":
    main()
