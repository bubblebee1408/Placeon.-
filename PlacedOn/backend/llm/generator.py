import asyncio
import random
import re
from typing import Any, Dict, List, Optional, Union

from backend.llm.ollama_client import call_ollama
from backend.schemas.generator_schema import GeneratorInput, PlanOutput, QuestionOutput
from backend.utils.json_utils import extract_json
from skill_taxonomy import display_skill, is_behavioral_skill

_GENERATOR_MODEL = "llama3"


def _default_question_type(action: str, skill: str) -> str:
    if skill.startswith("hr_"):
        return "hr_scenario"
    if is_behavioral_skill(skill):
        return "behavioral"
    if action == "challenge":
        return "system_design"
    if action == "help":
        return "conceptual"
    if action == "assess":
        return "conceptual"
    return "behavioral"


def _normalized_question(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9\s]", " ", value.lower())
    return re.sub(r"\s+", " ", normalized).strip()


def _is_duplicate_question(candidate: str, *previous: str) -> bool:
    normalized_candidate = _normalized_question(candidate)
    if not normalized_candidate:
        return False
    return any(normalized_candidate == _normalized_question(item) for item in previous if item)


def _looks_like_interviewer_question(text: str) -> bool:
    candidate = (text or "").strip().lower()
    if not candidate:
        return False

    # Hard reject obvious answer-like starts from candidate perspective.
    answer_like_starts = (
        "i ",
        "i'm ",
        "im ",
        "my ",
        "we ",
        "in my ",
    )
    if candidate.startswith(answer_like_starts):
        return False

    # Prefer explicit question punctuation, but also allow clear interviewer prompts.
    if "?" in candidate:
        return True

    interviewer_prompt_starts = (
        "tell me",
        "walk me",
        "can you",
        "could you",
        "how would",
        "what would",
        "why would",
        "explain",
        "describe",
        "nice",
        "great",
        "that's",
        "good",
        "okay so",
        "alright",
        "interesting",
        "so let",
        "let's",
        "imagine",
        "suppose",
    )
    return candidate.startswith(interviewer_prompt_starts)


def _fallback_prompt_variants(action: str, skill: str, difficulty: str = "medium") -> list[str]:
    label = display_skill(skill)
    if skill.startswith("hr_"):
        prompts: dict[str, list[str]] = {
            "help": [
                f"Let's look at {label}. Has there been a situation where you faced a tricky scenario with this? What happened?",
                f"How would you act in an HR scenario specifically involving {label}?",
                f"Can you provide a simple example of how you handle {label} in your daily work?",
            ],
            "probe": [
                f"Let's dive a bit deeper into that {label} scenario. What were the hidden stakes or ethical considerations?",
                f"In that situation involving {label}, how did you balance team morale against strict policies?",
                f"Tell me more about the outcome of that {label} approach. Were there any consequences?",
            ],
            "challenge": [
                f"Suppose your approach to {label} led to a major conflict with a manager. How do you resolve it?",
                f"If you were pushed to compromise your {label} by a tight deadline, what exact steps would you take?",
                f"Defend your handling of {label} in a scenario where another team member actively resists your viewpoint.",
            ],
            "assess": [
                f"How do you generally approach situations involving {label}? Can you share your philosophy?",
                f"What are the most common challenges you see regarding {label} in a typical workplace?",
                f"Describe your framework for dealing with {label}.",
            ],
        }
        return prompts.get(action, [f"Here is a scenario about {label}. How would you handle it?"])

    if is_behavioral_skill(skill):
        prompts: dict[str, list[str]] = {
            "help": [
                f"Let's make this concrete. Tell me about a real situation where you showed {label}. What happened?",
                f"Take one example that shows {label}. What was the situation, what did you do, and what changed?",
                f"Pick a specific moment related to {label}. Walk me through it step by step.",
            ],
            "probe": [
                f"Stay with that example on {label}. How did you decide what to do, and what signals guided you?",
                f"Go one level deeper on {label}. What trade-offs or tensions did you have to manage?",
                f"Walk me through how you handled {label} in practice and what you learned afterward.",
            ],
            "challenge": [
                f"Imagine a harder version of that {label} situation with time pressure and competing stakeholders. How would you handle it?",
                f"Defend your approach to {label} when the situation becomes more ambiguous or high-stakes.",
                f"If your first attempt at {label} failed, what would you change next and why?",
            ],
            "assess": [
                f"What experiences do you have dealing with {label} in past projects?",
                f"Can you give an overview of your approach to {label}?",
                f"Why is {label} an important trait for a modern engineer?"
            ],
        }
        return prompts.get(action, [f"Tell me about a real example that shows {label}."])

    # ── Technical Skills: Difficulty-Tiered Fallbacks ──
    easy_assess = [
        f"To kick things off — in your own words, what does {label} mean and when would you use it?",
        f"Let's start simple — can you walk me through the basics of {label}?",
        f"Before we go deeper — give me your quick take on what {label} is all about.",
    ]
    medium_assess = [
        f"Nice, so let's build on that. How would you actually apply {label} when building a real project?",
        f"That's a good foundation. Now, if you were working on a project and needed to use {label}, what approach would you take?",
        f"Cool. Can you walk me through a practical example of how you'd use {label} in a real codebase?",
    ]
    hard_assess = [
        f"Alright, let's push this further. Imagine you're building a production system and you hit a scaling issue with {label} — how would you debug and solve it?",
        f"Great understanding so far! Here's a scenario — your team's {label} implementation is causing performance bottlenecks under load. Walk me through your diagnosis and fix.",
        f"Interesting. Let's say you're designing a system from scratch and {label} is a core requirement but you have conflicting constraints. How do you navigate that?",
    ]

    if action == "assess":
        if difficulty == "easy":
            return easy_assess
        elif difficulty == "hard":
            return hard_assess
        else:
            return medium_assess

    prompts: dict[str, list[str]] = {
        "help": [
            f"No worries, let's simplify this. Can you walk me through the basics of {label} step by step?",
            f"That's okay! Let's break {label} down. What's the first thing that comes to mind when you think about it?",
            f"Let's take a step back. If you had to explain {label} to a junior developer, how would you do it?",
        ],
        "probe": [
            f"Great, you're on the right track! Let's go one level deeper — can you explain your {label} approach step by step?",
            f"That's solid. Now, in {label}, what's the key trade-off that guides your approach?",
            f"Nice answer! Walk me through your {label} thought process from first decision to final validation.",
        ],
        "challenge": [
            f"You clearly know your stuff here. Let's stress-test this — what happens to your {label} approach under realistic production constraints?",
            f"Good thinking! Now imagine one part of your {label} design fails in production at 3 AM. What's your runbook?",
            f"Strong answer. Can you defend your {label} approach against someone who argues the opposite trade-off?",
        ],
    }
    return prompts.get(action, [f"Let's check your knowledge on {label}. Explain your understanding."])


def _fallback_question(
    plan: PlanOutput,
    context: Optional[GeneratorInput] = None,
    mode: Optional[str] = None,
    skill: Optional[str] = None,
    difficulty: Optional[str] = None,
) -> QuestionOutput:
    mode = mode or plan.action
    skill = skill or plan.target_skill
    difficulty = difficulty or plan.difficulty

    variants = _fallback_prompt_variants(mode, skill, difficulty)
    question = variants[0]

    if context is not None:
        prev_a = context.last_question
        prev_b = context.previous_question

        for variant in variants:
            if not _is_duplicate_question(variant, prev_a, prev_b):
                question = variant
                break

    return QuestionOutput(
        question=question,
        skill=skill,
        difficulty=difficulty,
        type=_default_question_type(mode, skill),
    )


def _extract_answer_highlights(answer: str) -> list[str]:
    """Pull out key phrases from the candidate's answer to reference in transitions."""
    if not answer or len(answer) < 20:
        return []
    highlights = []
    # Look for specific things the candidate mentioned
    indicator_patterns = [
        r"(?:I |we |my team )(?:used|built|tried|implemented|set up|created)\s+([^,.!?]{5,40})",
        r"(?:like|such as|for example)\s+([^,.!?]{5,40})",
        r"(?:the key|important|main thing)\s+(?:is|was)\s+([^,.!?]{5,40})",
    ]
    for pattern in indicator_patterns:
        matches = re.findall(pattern, answer, re.IGNORECASE)
        for m in matches:
            cleaned = m.strip()
            if 5 <= len(cleaned) <= 50:
                highlights.append(cleaned)
    return highlights[:3]


def _build_tone_instruction(mode: str, difficulty: str, last_score: float, last_answer: str = "") -> str:
    """Build a tone/personality instruction block for the interviewer."""
    parts = []
    
    # --- TRANSITION BRIDGE (the key to human feel) ---
    # Reference the candidate's previous answer ~50% of the time to feel conversational
    # but not every time (that would feel forced)
    highlights = _extract_answer_highlights(last_answer)
    should_reference = random.random() < 0.5 and highlights and mode != "new"
    
    if last_score >= 0.75:
        if should_reference:
            ref = random.choice(highlights)
            parts.append(
                f"The candidate answered well and mentioned '{ref}'. "
                f"Start by briefly acknowledging that specific point — e.g., 'That's a really good point about {ref}' or "
                f"'I like how you brought up {ref}' — then smoothly transition into the next question. "
                "Keep the acknowledgment to ONE short sentence, not a paragraph."
            )
        else:
            parts.append(
                "The candidate answered the previous question well. "
                "Start with a brief, natural encouragement like 'Great answer!', 'That's solid', or "
                "'Nice, you clearly know this' — then transition smoothly. "
                "Keep it to ONE sentence max."
            )
    elif last_score >= 0.5:
        if should_reference:
            ref = random.choice(highlights)
            parts.append(
                f"The candidate gave a decent answer and mentioned '{ref}'. "
                f"Briefly acknowledge that point — e.g., 'Okay, I see what you mean about {ref}' — "
                "then transition naturally. Be warm but don't over-praise."
            )
        else:
            parts.append(
                "The candidate had a decent but not perfect previous answer. "
                "Be warm and neutral — 'Okay cool, let's keep going' or 'That's a fair point' — "
                "then move to the next question naturally."
            )
    elif last_score > 0.0:
        parts.append(
            "The candidate struggled with the previous question. "
            "Be supportive and non-judgmental — 'No worries, let me come at this from a different angle' or "
            "'That's okay, let's try something else' — make them feel safe to keep trying."
        )
    
    # --- CONVERSATIONAL STYLE ---
    parts.append(
        "IMPORTANT TONE RULES:\n"
        "- Sound like a friendly, experienced human interviewer — NOT a quiz bot.\n"
        "- NEVER start with 'What is the definition of...' or 'What is the primary goal of...' unless difficulty is easy.\n"
        "- Your question MUST start with a brief transition/reaction (1 sentence), THEN the actual question.\n"
        "- Vary your question openers. Do NOT always use 'Can you...' or 'What are some...'. "
        "Mix it up: 'Tell me about...', 'Walk me through...', 'Imagine...', 'So here's a scenario...', "
        "'What would happen if...', 'How did you handle...', 'Let's say...'\n"
        "- Keep it conversational — like two colleagues chatting, not an exam."
    )
    
    # --- DIFFICULTY GUIDANCE ---
    if difficulty == "easy":
        parts.append(
            "Ask a foundational question. It's okay to ask 'what is X' or 'explain the basics of X' at this level."
        )
    elif difficulty == "medium":
        parts.append(
            "Ask an applied/practical question. Focus on HOW they'd use it, not just WHAT it is. "
            "Example: 'If you were building X and needed Y, how would you approach it?'"
        )
    elif difficulty == "hard":
        parts.append(
            "Ask a scenario-based or deep-dive question. Present a real-world situation with constraints. "
            "Example: 'Imagine your team's X is failing under Y load — walk me through your debugging approach.'"
        )
    
    return "\n".join(parts)


def _build_probe_instruction(mode: str, probe_focus: list, judge_summary: str, last_answer: str) -> str:
    """Build a targeted probe instruction when following up on a weak answer."""
    if mode not in ("probe", "retry") and mode != "help":
        return ""
    
    parts = []
    
    if probe_focus:
        focus_items = ", ".join(probe_focus[:2])
        parts.append(
            f"\nPROBE TARGET: The candidate's previous answer was missing or weak on: [{focus_items}].\n"
            f"Your question MUST specifically target one of these gaps. Do NOT re-ask the same question. "
            f"Instead, ask about the SPECIFIC missing concept from a different angle.\n"
            f"Example: If they missed 'cache invalidation', ask 'What happens when stale data gets served to users?' "
            f"instead of repeating 'Explain caching'.\n"
        )
    
    if judge_summary:
        parts.append(
            f"JUDGE ASSESSMENT of previous answer: \"{judge_summary}\"\n"
            f"Use this to understand what the candidate knows vs. what they're missing, "
            f"and frame your follow-up to explore the gap.\n"
        )
    
    if last_answer and mode in ("probe", "retry"):
        # Extract a short snippet to reference
        snippet = last_answer[:120].strip()
        if len(last_answer) > 120:
            snippet += "..."
        parts.append(
            f"CANDIDATE'S PREVIOUS ANSWER (summary): \"{snippet}\"\n"
            f"Build on what they said. Pick up a specific claim or example they gave and push deeper, "
            f"OR approach the weak area from a scenario/example angle.\n"
        )
    
    return "\n".join(parts)


async def generate_question(
    plan: Union[PlanOutput, Dict[str, Any]],
    context: Dict[str, Any],
) -> QuestionOutput:
    plan_payload = plan.dict() if isinstance(plan, PlanOutput) else plan

    parsed_context = GeneratorInput.parse_obj(
        {
            **context,
            "plan": plan_payload,
        }
    )

    mode = str(plan_payload.get("action") or parsed_context.plan.action)
    target_skill = str(plan_payload.get("target_skill") or parsed_context.plan.target_skill)
    difficulty = str(plan_payload.get("difficulty") or parsed_context.plan.difficulty)
    default_type = _default_question_type(mode, target_skill)
    
    # Determine the candidate's last score from minimal_state for tone adaptation
    minimal_state = parsed_context.minimal_state or {}
    last_score = float(minimal_state.get("last_score", 0.0))
    # Also check skill_vector for current skill performance
    skill_vector = minimal_state.get("skill_vector", {})
    if isinstance(skill_vector, dict) and target_skill in skill_vector:
        skill_performance = float(skill_vector[target_skill])
        last_score = max(last_score, skill_performance)
    
    hr_instruction = ""
    if target_skill.startswith("hr_"):
        hr_instruction = "\nMake this question a tricky HR scenario-based situation. Focus on ethical, behavioral, or interpersonal conflicts, and make the candidate think critically about trade-offs."
    
    action_instruction = ""
    if mode == "assess":
        if difficulty == "hard":
            action_instruction = "\nAsk a scenario-based or system-design question that tests depth, trade-offs, and real-world application. Do NOT ask a basic definition question."
        elif difficulty == "medium":
            action_instruction = "\nAsk a practical, applied question — focus on how the candidate would USE this in a real project, not just define it."
        else:
            action_instruction = "\nStart with a conversational, foundational question to assess basic understanding. Keep it natural, not robotic."
    elif mode == "challenge":
        action_instruction = "\nPropose a complex, real-world scenario with constraints, edge cases, or trade-offs. Make the candidate think critically about a realistic production problem."
    elif mode == "help":
        action_instruction = "\nProvide a simpler, grounded question. Be warm and encouraging. Help the candidate demonstrate they know the basics."
    elif mode == "probe":
        action_instruction = "\nDig deeper into what the candidate just said. Ask a DIFFERENT follow-up that explores a specific gap or nuance — do NOT rephrase the same question."

    # Build conversational tone instruction (with answer-referencing)
    tone_instruction = _build_tone_instruction(mode, difficulty, last_score, parsed_context.last_answer)
    
    # Build targeted probe instruction from judge feedback
    probe_instruction = _build_probe_instruction(
        mode,
        parsed_context.probe_focus,
        parsed_context.judge_summary,
        parsed_context.last_answer,
    )

    prompt = f"""
You are a friendly, experienced human interviewer having a natural conversation. Generate one interview question in JSON.

--- YOUR PERSONALITY (FOLLOW THIS FIRST) ---
{tone_instruction}

--- QUESTION CONTEXT ---
mode: {mode}
topic: {target_skill}
difficulty: {difficulty}
last_question: {parsed_context.last_question}
previous_question: {parsed_context.previous_question}
{hr_instruction}{action_instruction}
{probe_instruction}

--- CRITICAL RULES ---
1. Your "question" field MUST begin with a short transition/reaction sentence (5-15 words), THEN the actual question.
   Good: "That's a solid point about retention. Now, imagine you're launching a new feature..."
   Bad: "Can you explain the basics of product metrics?"
2. Do NOT ask "What is the primary goal of..." or "What is the difference between..." unless difficulty is easy.
3. For probe/retry: you MUST ask a DIFFERENT question than last_question. Target the specific gap, don't rephrase.
4. Vary your question style. Use scenario-based, walk-me-through, imagine-you're, what-would-happen-if formats.

Return JSON only:
{{
  "question": "string (MUST start with a brief transition, then the question)",
  "skill": "string",
  "difficulty": "easy | medium | hard",
  "type": "conceptual | system_design | behavioral | hr_scenario"
}}
Set "type" to "{default_type}" unless it clearly does not fit.
"""
    
    # Higher temperature on probes/retries for more variety, lower on new assessments
    temperature = 0.45 if mode in ("probe", "help") else 0.25
    
    try:
        output = await asyncio.to_thread(
            call_ollama,
            prompt,
            _GENERATOR_MODEL,
            {
                "temperature": temperature,
                "top_p": 0.9,
                "num_predict": 128,  # More tokens to allow transition + question
                "timeout_seconds": 300,
            },
        )
        payload = extract_json(output)
        result = QuestionOutput.parse_obj(payload)
        if not _looks_like_interviewer_question(result.question):
            return _fallback_question(
                parsed_context.plan,
                parsed_context,
                mode=mode,
                skill=target_skill,
                difficulty=difficulty,
            )
        if _is_duplicate_question(result.question, parsed_context.last_question, parsed_context.previous_question):
            return _fallback_question(
                parsed_context.plan,
                parsed_context,
                mode=mode,
                skill=target_skill,
                difficulty=difficulty,
            )
        return result
    except Exception:  # noqa: BLE001
        return _fallback_question(
            parsed_context.plan,
            parsed_context,
            mode=mode,
            skill=target_skill,
            difficulty=difficulty,
        )
