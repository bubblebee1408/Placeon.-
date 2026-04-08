import asyncio
import re

from backend.llm.ollama_client import call_ollama
from backend.schemas.judge_schema import JudgeInput, JudgeOutput
from backend.utils.json_utils import extract_json

_JUDGE_MODEL = "llama3"

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
    "ttl",
    "invalidation",
    "cache key",
    "eviction",
    "retry",
    "backoff",
    "replication",
    "lock",
    "queue",
    "transaction",
)

_TRADEOFF_MARKERS = (
    "trade-off",
    "tradeoff",
    "however",
    "but",
    "latency",
    "consistency",
    "complexity",
    "cost",
    "stale",
    "memory",
    "edge case",
)

_TOOL_MARKERS = (
    "redis",
    "kafka",
    "rabbitmq",
    "mongodb",
    "postgres",
    "mysql",
    "memcached",
    "elasticsearch",
)


def build_judge_prompt(question: str, answer: str, prompt_template: str | None = None) -> str:
    if prompt_template:
        return prompt_template.format(question=question, answer=answer)

    return f"""
You are a strict and calibrated technical interview evaluator.

Your job is to evaluate a candidate's answer based on:
- correctness
- depth of understanding
- completeness
- clarity of explanation

---

# CORE PRINCIPLE

You MUST distinguish clearly between:
- shallow answers
- basic answers
- strong answers

Do NOT be generous.
Do NOT overestimate.

---

# CRITICAL RULE (MOST IMPORTANT)

If the answer ONLY mentions a tool, concept, or keyword (e.g., "use Redis")
WITHOUT explaining:
- how it works
- why it is used
- any trade-offs or details

Then:
-> score MUST be below 0.4

NEVER give medium or high scores to shallow answers.

---

# SCORING GUIDELINES (STRICT)

0.0 - 0.3:
- incorrect OR very shallow
- no explanation
- vague or generic statements

0.4 - 0.6:
- basic understanding
- some explanation
- limited depth
- missing important details

0.7 - 0.85:
- good answer
- clear reasoning
- some depth
- covers key ideas

0.85 - 1.0:
- strong answer
- deep understanding
- structured explanation
- includes trade-offs / edge cases

You MUST stay within these ranges.

---

# EVALUATION RULES

Penalize:
- vague answers
- missing reasoning
- lack of detail
- generic statements

Reward:
- clear explanations
- step-by-step thinking
- trade-offs
- real-world considerations

---

# CONFIDENCE RULE

- Weak or vague answers -> confidence MUST be <= 0.6
- Medium answers -> confidence around 0.5-0.75
- Strong answers -> confidence can be > 0.8

NEVER assign high confidence to weak answers.

---

# CONSISTENCY RULE

Ensure ranking:

shallow < basic < strong

Scores must reflect this ordering.

---

# FEW-SHOT CALIBRATION

Example 1:
Answer: "I use Redis"
Score: 0.2
Reason: Mentions tool but no explanation -> very shallow

Example 2:
Answer: "I use Redis with TTL for caching"
Score: 0.5
Reason: Basic understanding but limited depth

Example 3:
Answer: "I use Redis with TTL and cache invalidation strategies to handle stale data"
Score: 0.75
Reason: Good explanation with relevant concepts

Example 4:
Answer: "I use distributed caching with Redis, TTL, invalidation strategies, and consider trade-offs like consistency vs performance"
Score: 0.9
Reason: Deep, structured, and complete answer

---

# OUTPUT FORMAT (STRICT JSON ONLY)

{{
    "score": 0.0-1.0,
    "confidence": 0.0-1.0,
    "strengths": ["..."],
    "weaknesses": ["..."],
    "missing_concepts": ["..."]
}}

---

# FINAL RULE

Be strict, consistent, and calibrated.

Do NOT:
- over-score shallow answers
- give similar scores to different quality answers

Your evaluation must clearly separate weak, medium, and strong responses.

Before giving the final score, internally classify the answer as:
"shallow", "basic", or "strong", and ensure the score matches that category.

Question: {question}
Answer: {answer}
"""


def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _analyze_answer(answer: str) -> dict[str, bool | int]:
    normalized = answer.strip().lower()
    tokens = re.findall(r"\b\w[\w-]*\b", normalized)
    token_count = len(tokens)

    has_explanation = any(marker in normalized for marker in _EXPLANATION_MARKERS)
    has_mechanism = any(marker in normalized for marker in _MECHANISM_MARKERS)
    has_tradeoff = any(marker in normalized for marker in _TRADEOFF_MARKERS)
    mentions_tool = any(marker in normalized for marker in _TOOL_MARKERS)

    very_short = token_count <= 3
    keyword_only = token_count <= 6 and not has_explanation and not has_mechanism
    vague = token_count < 12 and not has_explanation and not has_mechanism

    return {
        "token_count": token_count,
        "has_explanation": has_explanation,
        "has_mechanism": has_mechanism,
        "has_tradeoff": has_tradeoff,
        "mentions_tool": mentions_tool,
        "very_short": very_short,
        "keyword_only": keyword_only,
        "vague": vague,
    }


def _calibrate_output(evaluation: JudgeOutput, answer: str) -> JudgeOutput:
    signals = _analyze_answer(answer)
    score = float(evaluation.score)
    confidence = float(evaluation.confidence)

    weaknesses = list(evaluation.weaknesses)
    missing = list(evaluation.missing_concepts)

    # Keep model judgment primary; only hard-cap obvious shallow responses.
    if bool(signals["very_short"]):
        if bool(signals["mentions_tool"]):
            score = min(score, 0.25)
        else:
            score = min(max(score, 0.25), 0.35)
        weaknesses.append("Answer is too short to demonstrate technical understanding.")
    elif bool(signals["keyword_only"]):
        if bool(signals["mentions_tool"]):
            score = min(score, 0.35)
            weaknesses.append("Mentions keywords without explaining mechanism or reasoning.")
        else:
            score = min(max(score, 0.25), 0.35)
            weaknesses.append("Generic statement lacks technical mechanism and reasoning.")
    elif bool(signals["vague"]):
        score = min(score, 0.50)

    # Mechanism-bearing answers should not collapse into shallow bands even if model is overly strict.
    if bool(signals["has_mechanism"]) and int(signals["token_count"]) >= 6 and score < 0.4:
        score = 0.45

    # Reward depth indicators with small nudges to avoid brittle rubric-only behavior.
    if bool(signals["has_explanation"]) and bool(signals["has_mechanism"]):
        score += 0.04
    if bool(signals["has_tradeoff"]):
        score += 0.05
    if int(signals["token_count"]) >= 35 and bool(signals["has_explanation"]):
        score += 0.03

    score = _clip(score)

    if score < 0.4:
        confidence = min(confidence, _WEAK_CONFIDENCE_MAX)
        if "How the approach works" not in missing:
            missing.append("How the approach works")
        if "Why this approach is appropriate" not in missing:
            missing.append("Why this approach is appropriate")
    elif score < 0.7:
        confidence = _clip(confidence, _MEDIUM_CONFIDENCE_MIN, _MEDIUM_CONFIDENCE_MAX)
    elif score >= 0.85:
        confidence = max(confidence, _STRONG_CONFIDENCE_MIN)

    return JudgeOutput(
        score=round(score, 3),
        confidence=round(_clip(confidence), 3),
        strengths=evaluation.strengths,
        weaknesses=list(dict.fromkeys(weaknesses)),
        missing_concepts=list(dict.fromkeys(missing)),
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
            "Clear technical explanation",
            "Reasoning and trade-offs",
        ],
    )


async def evaluate_answer(
    question: str,
    answer: str,
    prompt_template: str | None = None,
    model: str = _JUDGE_MODEL,
) -> JudgeOutput:
    judge_input = JudgeInput(question=question, answer=answer)
    prompt = build_judge_prompt(
        question=judge_input.question,
        answer=judge_input.answer,
        prompt_template=prompt_template,
    )
    output = await asyncio.to_thread(call_ollama, prompt, model)
    try:
        payload = extract_json(output)
        raw_evaluation = JudgeOutput.model_validate(payload)
    except Exception as exc:  # pragma: no cover - defensive against model format drift
        return _fallback_judge_output(exc)

    return _calibrate_output(raw_evaluation, judge_input.answer)
