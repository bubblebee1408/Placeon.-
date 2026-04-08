import json
from pathlib import Path
from typing import Any


def evaluate_prediction(predicted: dict[str, Any], expected: dict[str, float]) -> dict[str, Any]:
    score = float(predicted.get("score", 0.0))
    confidence = float(predicted.get("confidence", 0.0))

    score_error = abs(score - expected["quality_score"])
    confidence_error = abs(confidence - expected["confidence"])

    predicted_direction = _direction_bucket(score)
    expected_direction = _direction_bucket(expected["quality_score"])

    predicted_clarity = _estimate_predicted_clarity(predicted)
    clarity_error = abs(predicted_clarity - expected["clarity"])

    return {
        "score_error": round(score_error, 4),
        "confidence_error": round(confidence_error, 4),
        "clarity_error": round(clarity_error, 4),
        "direction_correct": predicted_direction == expected_direction,
        "predicted_direction": predicted_direction,
        "expected_direction": expected_direction,
    }


def aggregate_metrics(records: list[dict[str, Any]]) -> dict[str, float]:
    if not records:
        return {
            "avg_score_error": 0.0,
            "avg_confidence_error": 0.0,
            "avg_clarity_error": 0.0,
            "direction_accuracy": 0.0,
        }

    total = float(len(records))
    score_sum = sum(item["errors"]["score_error"] for item in records)
    confidence_sum = sum(item["errors"]["confidence_error"] for item in records)
    clarity_sum = sum(item["errors"]["clarity_error"] for item in records)
    direction_hits = sum(1 for item in records if item["errors"]["direction_correct"])

    return {
        "avg_score_error": round(score_sum / total, 4),
        "avg_confidence_error": round(confidence_sum / total, 4),
        "avg_clarity_error": round(clarity_sum / total, 4),
        "direction_accuracy": round(direction_hits / total, 4),
    }


def select_failures(
    records: list[dict[str, Any]],
    score_error_threshold: float = 0.25,
    confidence_error_threshold: float = 0.25,
    limit: int = 25,
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []

    for record in records:
        errors = record["errors"]
        if (
            errors["score_error"] >= score_error_threshold
            or errors["confidence_error"] >= confidence_error_threshold
            or not errors["direction_correct"]
        ):
            failures.append(record)

    failures.sort(
        key=lambda row: (
            row["errors"]["score_error"],
            row["errors"]["confidence_error"],
            0.0 if row["errors"]["direction_correct"] else 1.0,
        ),
        reverse=True,
    )
    return failures[:limit]


def write_failures(path: str, failures: list[dict[str, Any]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(failures, indent=2), encoding="utf-8")


def _direction_bucket(score: float) -> str:
    return "good" if score >= 0.6 else "bad"


def _estimate_predicted_clarity(predicted: dict[str, Any]) -> float:
    strengths = " ".join(predicted.get("strengths", [])).lower()
    weaknesses = " ".join(predicted.get("weaknesses", [])).lower()

    clarity = 0.5
    if any(token in strengths for token in ["clear", "structured", "specific", "trade-off"]):
        clarity += 0.25
    if any(token in weaknesses for token in ["vague", "unclear", "generic", "missing detail"]):
        clarity -= 0.25

    return max(0.0, min(1.0, clarity))
