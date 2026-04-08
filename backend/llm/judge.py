import asyncio

from backend.llm.ollama_client import call_ollama
from backend.schemas.judge_schema import JudgeInput, JudgeOutput
from backend.utils.json_utils import extract_json

_JUDGE_MODEL = "llama3"


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
    payload = extract_json(output)
    return JudgeOutput.model_validate(payload)
