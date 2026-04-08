import csv
import json
from pathlib import Path
from typing import Any

_TEXT_KEYS = [
    "input_text",
    "text",
    "answer",
    "response",
    "content",
    "essay",
]

_SCORE_KEYS = [
    "quality_score",
    "score",
    "label",
    "rating",
    "target",
    "quality",
]

_CONFIDENCE_KEYS = ["confidence", "certainty", "label_confidence"]
_CLARITY_KEYS = ["clarity", "readability", "coherence"]

_LABEL_MAP = {
    "very bad": 0.05,
    "bad": 0.15,
    "weak": 0.25,
    "poor": 0.25,
    "average": 0.5,
    "okay": 0.55,
    "good": 0.75,
    "strong": 0.85,
    "excellent": 0.95,
}


def load_kaggle_dataset(dataset_path: str, limit: int | None = None) -> list[dict[str, Any]]:
    """Load common Kaggle text datasets (.csv, .json, .jsonl) into a unified format."""
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        raw_records = _load_csv(path)
    elif suffix in {".json", ".jsonl"}:
        raw_records = _load_json(path)
    else:
        raise ValueError("Unsupported dataset format. Use .csv, .json, or .jsonl")

    normalized = [_normalize_record(record) for record in raw_records]
    filtered = [record for record in normalized if record is not None]
    if limit is not None:
        return filtered[:limit]
    return filtered


def _load_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _load_json(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        rows: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)

    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if "data" in payload and isinstance(payload["data"], list):
            return payload["data"]
        return [payload]
    raise ValueError("Unsupported JSON shape. Expected list[dict] or dict")


def _normalize_record(record: dict[str, Any]) -> dict[str, Any] | None:
    input_text = _first_non_empty(record, _TEXT_KEYS)
    if not input_text:
        return None

    quality_score = _normalize_score(_first_non_empty(record, _SCORE_KEYS))
    confidence = _normalize_score(_first_non_empty(record, _CONFIDENCE_KEYS))
    clarity = _normalize_score(_first_non_empty(record, _CLARITY_KEYS))

    if quality_score is None:
        quality_score = _infer_quality_from_text(input_text)
    if confidence is None:
        confidence = _infer_confidence_from_score(quality_score)
    if clarity is None:
        clarity = _infer_clarity_from_text(input_text)

    return {
        "input_text": input_text,
        "expected": {
            "quality_score": _clip01(quality_score),
            "confidence": _clip01(confidence),
            "clarity": _clip01(clarity),
        },
    }


def _first_non_empty(record: dict[str, Any], keys: list[str]) -> Any | None:
    for key in keys:
        if key in record and record[key] not in (None, ""):
            return record[key]
    return None


def _normalize_score(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, str):
        text = value.strip().lower()
        if text in _LABEL_MAP:
            return _LABEL_MAP[text]
        try:
            value = float(text)
        except ValueError:
            return None

    if isinstance(value, bool):
        return 1.0 if value else 0.0

    if isinstance(value, (int, float)):
        numeric = float(value)
        if 0.0 <= numeric <= 1.0:
            return numeric
        if 1.0 <= numeric <= 5.0:
            return (numeric - 1.0) / 4.0
        if 0.0 <= numeric <= 10.0:
            return numeric / 10.0
        if 0.0 <= numeric <= 100.0:
            return numeric / 100.0
        return _clip01(numeric)

    return None


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _infer_quality_from_text(text: str) -> float:
    length = len(text.split())
    if length < 6:
        return 0.25
    if length < 16:
        return 0.45
    if length < 35:
        return 0.65
    return 0.8


def _infer_confidence_from_score(score: float) -> float:
    # Encourage calibrated confidence near strong signals and uncertainty near middle scores.
    distance_from_mid = abs(score - 0.5)
    return _clip01(0.45 + distance_from_mid)


def _infer_clarity_from_text(text: str) -> float:
    words = text.split()
    if not words:
        return 0.0

    vague_terms = {"maybe", "probably", "kind", "stuff", "things", "somehow"}
    vague_hits = sum(1 for word in words if word.lower().strip(".,!?") in vague_terms)
    punctuation_bonus = 0.08 if any(token in text for token in [".", ":", ";"]) else 0.0

    base = min(1.0, len(words) / 40.0)
    clarity = base + punctuation_bonus - (vague_hits * 0.06)
    return _clip01(clarity)
