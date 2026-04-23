import asyncio
import logging
import re
from typing import Dict, Optional, Union

from backend.llm.ollama_client import call_ollama
from backend.schemas.judge_schema import JudgeInput, JudgeOutput
from backend.utils.json_utils import extract_json

_JUDGE_MODEL = "gemma3:1b"
_LOGGER = logging.getLogger(__name__)

_WEAK_CONFIDENCE_MAX = 0.6
_MEDIUM_CONFIDENCE_MIN = 0.5
_MEDIUM_CONFIDENCE_MAX = 0.75
_STRONG_CONFIDENCE_MIN = 0.8

_EXPLANATION_MARKERS = (
    "because",
    "so that",
    "using",
    "through",
    "works by",
    "ensures",
    "to avoid",
)

_MECHANISM_MARKERS = (
    "ttl", "invalidation", "cache key", "eviction", "retry", "backoff", "replication",
    "lock", "queue", "transaction", "partition", "shard", "indexing",
    # Psychological/Behavioral markers
    "because", "therefore", "as a result", "which led to", "i decided", "i realised",
    "i recognised", "my approach was", "the reason was", "what i changed was",
    "i learned that", "the pattern i noticed", "i reflected on", "i understood",
    "asked", "aligned", "followed up", "listened", "coached", "delegated",
    "de-escalated", "prioritized", "validated", "owned", "accountability",
)

_TRADEOFF_MARKERS = (
    "trade-off", "tradeoff", "however", "but", "latency", "consistency", "complexity",
    "cost", "stale", "memory", "edge case", "stakeholder", "deadline", "pressure",
    "constraint", "conflict", "balance",
    # Psychological/Behavioral markers
    "on one hand", "the cost was", "the risk was", "i had to balance", "i sacrificed",
    "short term vs long term", "not ideal but", "i chose x over y", "despite the downside",
)

_DEPTH_INDICATORS = (
    "specifically", "for example", "in that instance", "concretely", "the exact moment was",
    "what i actually did", "the outcome was", "i measured", "i tracked", "i followed up",
    "i verified", "to give you a concrete", "in practice", "when i applied",
)

_SHALLOW_INDICATORS = (
    "i always try my best", "i am a hard worker", "i give 100 percent", "i am very passionate",
    "i believe in teamwork", "i am a quick learner", "communication is key", "i work well under pressure",
    "i am very motivated", "i always stay positive",
)

_TOOL_MARKERS = (
    "redis", "kafka", "rabbitmq", "mongodb", "postgres", "mysql", "memcached",
    "elasticsearch", "slack", "jira", "1:1", "retro", "gh actions", "jenkins",
)


def build_judge_prompt(question: str, answer: str, prompt_template: Optional[str] = None) -> str:
    if prompt_template:
        return prompt_template.replace("{question}", question).replace("{answer}", answer)

    return f"""
Evaluate the interview answer strictly.
The answer may be technical or behavioral.
Do not reward buzzwords, personality claims, or confidence style without evidence.
Concrete examples, mechanisms, reasoning, and trade-offs should raise the score.
Keyword-only answers without explanation must score below 0.4.

Return JSON only:
{{
  "score": 0.0-1.0,
  "confidence": 0.0-1.0,
  "strengths": ["..."],
  "weaknesses": ["..."],
  "missing_concepts": ["..."],
  "intent": "no_understanding | partial_understanding | clear_understanding",
  "depth": "shallow | basic | good | strong",
  "clarity": "poor | okay | clear",
  "atomic_summary": "a 1-sentence high-density summary of the core insight/state gained about the candidate's skill"
}}

Question: {question}
Answer: {answer}
"""


def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _analyze_answer(answer: str) -> Dict[str, Union[bool, int]]:
    normalized = answer.strip().lower()
    tokens = re.findall(r"\b\w[\w-]*\b", normalized)
    token_count = len(tokens)

    has_explanation = any(marker in normalized for marker in _EXPLANATION_MARKERS)
    has_mechanism = any(marker in normalized for marker in _MECHANISM_MARKERS)
    has_tradeoff = any(marker in normalized for marker in _TRADEOFF_MARKERS)
    mentions_tool = any(marker in normalized for marker in _TOOL_MARKERS)
    has_example = any(marker in normalized for marker in _DEPTH_INDICATORS)
    has_shallow = any(marker in normalized for marker in _SHALLOW_INDICATORS)

    very_short = token_count <= 3
    keyword_only = token_count <= 6 and not has_explanation and not has_mechanism and not has_example
    vague = token_count < 12 and not has_explanation and not has_mechanism and not has_example

    return {
        "token_count": token_count,
        "has_explanation": has_explanation,
        "has_mechanism": has_mechanism,
        "has_tradeoff": has_tradeoff,
        "mentions_tool": mentions_tool,
        "has_example": has_example,
        "has_shallow": has_shallow,
        "very_short": very_short,
        "keyword_only": keyword_only,
        "vague": vague,
    }


def _depth_from_score(score: float) -> str:
    if score < 0.35:
        return "shallow"
    if score < 0.6:
        return "basic"
    if score < 0.8:
        return "good"
    return "strong"


def _clarity_from_signals(signals: Dict[str, Union[bool, int]]) -> str:
    token_count = int(signals["token_count"])
    if bool(signals["very_short"]) or bool(signals["keyword_only"]) or bool(signals["vague"]):
        return "poor"
    if (
        bool(signals["has_explanation"])
        and (bool(signals["has_mechanism"]) or bool(signals["has_example"]))
        and token_count >= 12
    ):
        return "clear"
    return "okay"


def _intent_from_signals(signals: Dict[str, Union[bool, int]], score: float) -> str:
    if bool(signals["very_short"]) or bool(signals["keyword_only"]):
        return "no_understanding"

    has_substance = (
        bool(signals["has_explanation"])
        or bool(signals["has_mechanism"])
        or bool(signals["has_example"])
    )
    if has_substance and score >= 0.72 and (bool(signals["has_tradeoff"]) or int(signals["token_count"]) >= 18):
        return "clear_understanding"

    if has_substance:
        return "partial_understanding"

    if score < 0.35:
        return "no_understanding"
    return "partial_understanding"


def _calibrate_output(evaluation: JudgeOutput, answer: str) -> JudgeOutput:
    signals = _analyze_answer(answer)
    score = float(evaluation.score)
    confidence = float(evaluation.confidence)

    _LOGGER.debug("Judge raw score=%s tokens=%s", score, signals["token_count"])

    weaknesses = list(evaluation.weaknesses)
    missing = list(evaluation.missing_concepts)

    # Keep model judgment primary; only hard-cap obvious shallow responses.
    if bool(signals["very_short"]):
        old_score = score
        if bool(signals["mentions_tool"]):
            score = min(score, 0.25)
        else:
            score = min(max(score, 0.25), 0.35)
        _LOGGER.debug("Judge penalty very_short: %s -> %s", old_score, score)
        weaknesses.append("Answer is too short to demonstrate substantive understanding.")
    elif bool(signals["keyword_only"]):
        old_score = score
        if bool(signals["mentions_tool"]):
            score = min(score, 0.35)
            weaknesses.append("Mentions keywords without explaining mechanism, example, or reasoning.")
        else:
            score = min(max(score, 0.25), 0.35)
            weaknesses.append("Generic statement lacks concrete evidence, mechanism, or reasoning.")
        _LOGGER.debug("Judge penalty keyword_only: %s -> %s", old_score, score)
    elif bool(signals["vague"]):
        score = min(score, 0.50)
        _LOGGER.debug("Judge penalty vague: capped at 0.50")

    # Penalize purely shallow buzzword statements
    if bool(signals["has_shallow"]) and not bool(signals["has_mechanism"]) and not bool(signals["has_example"]):
        old_score = score
        score = min(score, 0.45)
        _LOGGER.debug("Judge penalty shallow_buzzword: %s -> %s", old_score, score)
        weaknesses.append("Uses generic buzzwords without providing concrete evidence or mechanisms.")

    # Mechanism-bearing answers should not collapse into shallow bands even if model is overly strict.
    if (bool(signals["has_mechanism"]) or bool(signals["has_example"])) and int(signals["token_count"]) >= 6 and score < 0.4:
        score = 0.45
        _LOGGER.debug("Judge rescue mechanism-bearing answer raised to 0.45")

    # Reward depth indicators with small nudges to avoid brittle rubric-only behavior.
    if bool(signals["has_explanation"]) and bool(signals["has_mechanism"]):
        score += 0.04
    if bool(signals["has_example"]):
        score += 0.03
    if bool(signals["has_tradeoff"]):
        score += 0.05
    if int(signals["token_count"]) >= 35 and bool(signals["has_explanation"]):
        score += 0.03

    score = _clip(score)
    _LOGGER.debug("Judge final calibrated score=%s", score)

    depth = _depth_from_score(score)
    clarity = _clarity_from_signals(signals)
    intent = _intent_from_signals(signals, score)

    if score < 0.4:
        confidence = min(confidence, _WEAK_CONFIDENCE_MAX)
        if "How the approach works" not in missing:
            missing.append("How the approach works")
        if "Concrete example or reasoning" not in missing:
            missing.append("Concrete example or reasoning")
    elif score < 0.7:
        confidence = _clip(confidence, _MEDIUM_CONFIDENCE_MIN, _MEDIUM_CONFIDENCE_MAX)
    elif score >= 0.85:
        confidence = max(confidence, _STRONG_CONFIDENCE_MIN)

    # Keep confidence bands aligned with the inferred depth bucket.
    if depth == "shallow":
        confidence = min(confidence, 0.55)
    elif depth == "basic":
        confidence = _clip(confidence, 0.5, 0.72)
    elif depth == "good":
        confidence = _clip(confidence, 0.65, 0.85)
    else:
        confidence = max(confidence, _STRONG_CONFIDENCE_MIN)

    if clarity == "poor" and "Clear explanation of approach" not in missing:
        missing.append("Clear explanation of approach")

    return JudgeOutput(
        score=round(score, 3),
        confidence=round(_clip(confidence), 3),
        strengths=evaluation.strengths,
        weaknesses=list(dict.fromkeys(weaknesses)),
        missing_concepts=list(dict.fromkeys(missing)),
        intent=intent,
        depth=depth,
        clarity=clarity,
        atomic_summary=evaluation.atomic_summary,
    )


def _fallback_judge_output(error: Exception) -> JudgeOutput:
    return JudgeOutput(
        score=0.2,
        confidence=0.55,
        strengths=[],
        weaknesses=[
            "Judge output parsing failed; defaulting to conservative evaluation.",
            f"Parsing error: {type(error).__name__}",
        ],
        missing_concepts=[
            "Clear explanation of the approach",
            "Evidence, reasoning, and trade-offs",
        ],
        intent="no_understanding",
        depth="shallow",
        clarity="poor",
    )


async def evaluate_answer(
    question: str,
    answer: str,
    prompt_template: Optional[str] = None,
    model: str = _JUDGE_MODEL,
) -> JudgeOutput:
    judge_input = JudgeInput(question=question, answer=answer)
    prompt = build_judge_prompt(
        question=judge_input.question,
        answer=judge_input.answer,
        prompt_template=prompt_template,
    )
    try:
        output = await asyncio.to_thread(
            call_ollama,
            prompt,
            model,
            {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 128,
                "timeout_seconds": 12,
            },
        )
        payload = extract_json(output)
        raw_evaluation = JudgeOutput.model_validate(payload)
    except Exception as exc:  # pragma: no cover - defensive against model format drift
        return _fallback_judge_output(exc)

    return _calibrate_output(raw_evaluation, judge_input.answer)
