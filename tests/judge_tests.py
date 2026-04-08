import argparse
import asyncio
from dataclasses import dataclass

from backend.llm.judge import evaluate_answer

STRICT_MODE = True
DEFAULT_QUESTION = "How would you design a caching strategy for a backend system?"


@dataclass
class JudgeBehaviorCase:
    input_text: str
    expected_score_range: tuple[float, float]
    description: str


TEST_CASES = [
    JudgeBehaviorCase(
        input_text="I use Redis",
        expected_score_range=(0.0, 0.4),
        description="very shallow answer",
    ),
    JudgeBehaviorCase(
        input_text="I use Redis with TTL for caching",
        expected_score_range=(0.4, 0.7),
        description="basic but acceptable answer",
    ),
    JudgeBehaviorCase(
        input_text="I use Redis with TTL and implement cache invalidation strategies to handle stale data",
        expected_score_range=(0.7, 1.0),
        description="strong and complete answer",
    ),
    JudgeBehaviorCase(
        input_text="I am not sure how caching works",
        expected_score_range=(0.0, 0.3),
        description="lack of knowledge",
    ),
    JudgeBehaviorCase(
        input_text="Caching improves performance",
        expected_score_range=(0.2, 0.5),
        description="generic statement without depth",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Behavior validation suite for tuned AI judge")
    parser.add_argument("--model", default="llama3", help="Ollama model to use")
    parser.add_argument("--question", default=DEFAULT_QUESTION, help="Evaluation context question")
    parser.add_argument("--strict", action="store_true", help="Enable strict mode")
    return parser.parse_args()


def apply_score_range_mode(score_range: tuple[float, float], strict_mode: bool) -> tuple[float, float]:
    if not strict_mode:
        return score_range

    low, high = score_range
    # Narrow boundaries in strict mode to increase calibration pressure.
    return max(0.0, low + 0.05), min(1.0, high - 0.05)


def is_weak_case(case: JudgeBehaviorCase) -> bool:
    return case.expected_score_range[1] <= 0.4


def is_strong_case(case: JudgeBehaviorCase) -> bool:
    return case.expected_score_range[0] >= 0.7


def confidence_bounds(strict_mode: bool) -> tuple[float, float]:
    if strict_mode:
        return 0.7, 0.4
    return 0.8, 0.3


def build_failure_insights(reasons: list[str]) -> list[str]:
    insights: list[str] = []
    for reason in reasons:
        if "score_out_of_range" in reason:
            insights.append("Model scoring is not aligned with expected calibration boundaries.")
        if "over_scoring_shallow" in reason:
            insights.append("Model is over-scoring shallow answers.")
        if "high_confidence_weak" in reason:
            insights.append("Model confidence too high for weak answer.")
        if "low_confidence_strong" in reason:
            insights.append("Model not confident enough on strong evidence.")
        if "depth_not_rewarded" in reason:
            insights.append("Model not rewarding depth and concrete mechanisms.")
    return sorted(set(insights))


async def run_behavior_suite(model: str, question: str, strict_mode: bool) -> int:
    weak_conf_high, strong_conf_low = confidence_bounds(strict_mode)

    total = len(TEST_CASES)
    passed = 0
    failures: list[dict[str, object]] = []
    case_scores: list[float] = []

    print("=== Judge Behavior Validation ===")
    print(f"STRICT_MODE={strict_mode}")
    print(f"MODEL={model}")
    print()

    for index, case in enumerate(TEST_CASES, start=1):
        effective_range = apply_score_range_mode(case.expected_score_range, strict_mode)
        result = await evaluate_answer(question=question, answer=case.input_text, model=model)

        score = float(result.score)
        confidence = float(result.confidence)
        case_scores.append(score)

        reasons: list[str] = []
        if not (effective_range[0] <= score <= effective_range[1]):
            reasons.append("score_out_of_range")

        if is_weak_case(case) and confidence > weak_conf_high:
            reasons.append("high_confidence_weak")

        if is_strong_case(case) and confidence < strong_conf_low:
            reasons.append("low_confidence_strong")

        if case.description in {"very shallow answer", "generic statement without depth"} and score > effective_range[1]:
            reasons.append("over_scoring_shallow")

        if case.description == "strong and complete answer" and score < effective_range[0]:
            reasons.append("depth_not_rewarded")

        status = "PASS" if not reasons else "FAIL"
        if status == "PASS":
            passed += 1

        print(f"[{index}] {status} - {case.description}")
        print(f"Input: {case.input_text}")
        print(f"Predicted score: {score:.3f}")
        print(f"Expected range: [{effective_range[0]:.2f}, {effective_range[1]:.2f}]")
        print(f"Confidence: {confidence:.3f}")
        print(f"Strengths: {result.strengths[:3]}")
        print(f"Weaknesses: {result.weaknesses[:3]}")

        if reasons:
            insights = build_failure_insights(reasons)
            print("Reason: " + "; ".join(reasons))
            for insight in insights:
                print(f"Suggestion: {insight}")
            failures.append(
                {
                    "description": case.description,
                    "input": case.input_text,
                    "score": score,
                    "confidence": confidence,
                    "expected_range": list(effective_range),
                    "reasons": reasons,
                    "suggestions": insights,
                }
            )
        print("-" * 72)

    # Monotonicity sanity check for no-random-scoring behavior.
    shallow = case_scores[0]
    medium = case_scores[1]
    strong = case_scores[2]
    monotonic_ok = shallow <= medium <= strong
    if not monotonic_ok:
        print("Monotonic check: FAIL")
        print("Reason: Judge is not consistently ranking shallow/basic/strong answers.")
        print("Suggestion: tighten prompt boundaries and few-shot examples for rank ordering.")
        failures.append(
            {
                "description": "monotonic_ranking",
                "input": "N/A",
                "score": [round(shallow, 3), round(medium, 3), round(strong, 3)],
                "confidence": None,
                "expected_range": "shallow <= basic <= strong",
                "reasons": ["ranking_inconsistency"],
                "suggestions": ["Improve prompt calibration to enforce stable ranking."],
            }
        )
    else:
        print("Monotonic check: PASS")

    failed = total - passed
    failure_pct = (failed / total) * 100.0

    print()
    print("=== Summary ===")
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Failure percentage: {failure_pct:.2f}%")

    if failures:
        print()
        print("=== Failure Insights ===")
        for item in failures:
            print(f"Case: {item['description']}")
            print("Why it failed: " + "; ".join(item["reasons"]))
            for suggestion in item["suggestions"]:
                print(f"Suggestion: {suggestion}")
            print("-" * 72)

    return 0 if failed == 0 and monotonic_ok else 1


def main() -> None:
    args = parse_args()
    strict_mode = bool(args.strict or STRICT_MODE)
    exit_code = asyncio.run(run_behavior_suite(model=args.model, question=args.question, strict_mode=strict_mode))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
