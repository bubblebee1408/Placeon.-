import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from training.data_adapter import load_kaggle_dataset
from training.evaluator import aggregate_metrics, select_failures, write_failures
from training.run_judge import run_judge_on_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prompt-driven judge calibration pipeline")
    parser.add_argument("--dataset", required=True, help="Path to Kaggle-style dataset (.csv, .json, .jsonl)")
    parser.add_argument("--question", default="Evaluate this technical answer.", help="Judge question context")
    parser.add_argument("--iterations", type=int, default=3, help="Number of prompt-improvement rounds")
    parser.add_argument("--limit", type=int, default=120, help="Maximum samples to load")
    parser.add_argument("--model", default="llama3", help="Ollama model name")
    parser.add_argument("--failure-path", default="training/failures.json", help="Failure log output path")
    parser.add_argument(
        "--report-path",
        default="training/improvement_report.json",
        help="Improvement summary output path",
    )
    return parser.parse_args()


def build_prompt(iteration: int, feedback: dict[str, Any] | None = None) -> str:
    base_prompt = """
You are a strict evaluator for technical interview answers.

Task:
- Evaluate only answer quality signal: clarity, depth, completeness, and trade-offs.
- Do not reward personality traits, confidence style, or verbosity alone.
- Separate weak, partial, and strong answers with clear score boundaries.

Scoring:
- 0.0-0.3: weak answer, vague or mostly incorrect.
- 0.4-0.7: partially correct, some useful content but missing key concepts.
- 0.8-1.0: strong answer with specific implementation detail and trade-off reasoning.

Return ONLY JSON:
{{
  "score": 0.0-1.0,
  "confidence": 0.0-1.0,
  "strengths": ["string"],
  "weaknesses": ["string"],
  "missing_concepts": ["string"]
}}

Question: {question}
Answer: {answer}
""".strip()

    if iteration <= 1:
        return base_prompt

    rules_block = """
Additional calibration rules:
- Penalize vague answers and generic recommendations.
- Penalize missing key concepts required for correctness.
- Reward structured reasoning with steps, mechanisms, and failure handling.
- Reward depth and explicit trade-offs.
- Avoid over-scoring fluent but shallow answers.
- Confidence must track evidence quality: low evidence => low confidence.
""".strip()

    prompt = f"{base_prompt}\n\n{rules_block}"

    if iteration >= 3:
        few_shot_block = """
Calibration examples:
Example 1
Answer: "Use Redis"
Expected score: 0.3
Reason: tool mention only, no mechanism or constraints.

Example 2
Answer: "Use Redis with TTL and invalidation"
Expected score: 0.7
Reason: practical mechanism included but shallow trade-off analysis.

Example 3
Answer: "Use distributed cache with consistency trade-offs, invalidation strategy, and fallback on cache miss"
Expected score: 0.9
Reason: covers architecture depth and trade-off reasoning.
""".strip()
        prompt = f"{prompt}\n\n{few_shot_block}"

    if feedback:
        adaptive_rules = []
        if feedback.get("overscore_rate", 0.0) > 0.2:
            adaptive_rules.append("Apply a stronger penalty to generic or buzzword-only answers.")
        if feedback.get("underscore_rate", 0.0) > 0.2:
            adaptive_rules.append("Do not under-score answers that include concrete mechanisms and trade-offs.")
        if feedback.get("confidence_miscalibration", 0.0) > 0.2:
            adaptive_rules.append("Reduce confidence when key concepts are missing; increase only with explicit evidence.")

        if adaptive_rules:
            prompt = f"{prompt}\n\nAdaptive corrections:\n- " + "\n- ".join(adaptive_rules)

    return prompt


def build_feedback(failures: list[dict[str, Any]]) -> dict[str, float]:
    if not failures:
        return {
            "overscore_rate": 0.0,
            "underscore_rate": 0.0,
            "confidence_miscalibration": 0.0,
        }

    total = float(len(failures))
    overscored = 0
    underscored = 0
    confidence_bad = 0

    for item in failures:
        predicted_score = float(item["predicted"]["score"])
        expected_score = float(item["expected"]["quality_score"])
        if predicted_score - expected_score >= 0.25:
            overscored += 1
        if expected_score - predicted_score >= 0.25:
            underscored += 1
        if item["errors"]["confidence_error"] >= 0.25:
            confidence_bad += 1

    return {
        "overscore_rate": round(overscored / total, 4),
        "underscore_rate": round(underscored / total, 4),
        "confidence_miscalibration": round(confidence_bad / total, 4),
    }


def summarize_iteration(iteration: int, metrics: dict[str, float], failures: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "iteration": iteration,
        "metrics": metrics,
        "failure_count": len(failures),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


def choose_best_iteration(iteration_reports: list[dict[str, Any]]) -> dict[str, Any]:
    def composite(report: dict[str, Any]) -> float:
        metrics = report["metrics"]
        return (
            metrics["avg_score_error"] * 0.5
            + metrics["avg_confidence_error"] * 0.25
            + metrics["avg_clarity_error"] * 0.1
            + (1.0 - metrics["direction_accuracy"]) * 0.15
        )

    return min(iteration_reports, key=composite)


def main() -> None:
    args = parse_args()

    dataset = load_kaggle_dataset(args.dataset, limit=args.limit)
    if not dataset:
        raise ValueError("No valid rows found after normalization")

    feedback: dict[str, float] | None = None
    reports: list[dict[str, Any]] = []
    best_failures: list[dict[str, Any]] = []

    for iteration in range(1, args.iterations + 1):
        prompt = build_prompt(iteration=iteration, feedback=feedback)
        records = asyncio.run(
            run_judge_on_dataset(
                dataset=dataset,
                question=args.question,
                prompt_template=prompt,
                model=args.model,
            )
        )

        metrics = aggregate_metrics(records)
        failures = select_failures(records)
        reports.append(summarize_iteration(iteration=iteration, metrics=metrics, failures=failures))

        feedback = build_feedback(failures)
        if iteration == args.iterations:
            best_failures = failures

        print(
            f"iter={iteration} "
            f"avg_score_error={metrics['avg_score_error']:.4f} "
            f"avg_conf_error={metrics['avg_confidence_error']:.4f} "
            f"direction_acc={metrics['direction_accuracy']:.4f} "
            f"failures={len(failures)}"
        )

    best_iteration = choose_best_iteration(reports)
    write_failures(args.failure_path, best_failures)

    report_path = Path(args.report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "dataset_size": len(dataset),
        "best_iteration": best_iteration,
        "iterations": reports,
        "summary": {
            "final_avg_score_error": reports[-1]["metrics"]["avg_score_error"],
            "final_avg_confidence_error": reports[-1]["metrics"]["avg_confidence_error"],
            "final_direction_accuracy": reports[-1]["metrics"]["direction_accuracy"],
        },
    }
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("\nImprovement summary")
    print(json.dumps(payload["summary"], indent=2))
    print(f"Best iteration: {best_iteration['iteration']}")
    print(f"Failure log: {args.failure_path}")
    print(f"Report: {args.report_path}")


if __name__ == "__main__":
    main()
