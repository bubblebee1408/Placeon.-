#!/usr/bin/env python3
"""
PlacedOn — Live Junior AI Intern Interview Simulation
Simulates a full interview in the terminal with typing animations.
The AI acts as the CANDIDATE being interviewed about the PlacedOn codebase.
"""

import sys
import time
import random

# ── Terminal Colors ──
class C:
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_RED = "\033[41m"
    BG_YELLOW = "\033[43m"
    RESET = "\033[0m"


def type_text(text, speed=0.012, color=""):
    """Simulate typing effect."""
    for char in text:
        sys.stdout.write(f"{color}{char}{C.RESET}")
        sys.stdout.flush()
        if char in ".!?":
            time.sleep(speed * 8)
        elif char == ",":
            time.sleep(speed * 4)
        elif char == "\n":
            time.sleep(speed * 3)
        else:
            time.sleep(speed + random.uniform(-0.005, 0.005))
    print()


def fast_print(text, color=""):
    """Print with slight delay per line for readability."""
    for line in text.split("\n"):
        print(f"{color}{line}{C.RESET}")
        time.sleep(0.05)


def banner(text, color=C.CYAN):
    width = 70
    border = "═" * width
    print(f"\n{color}{C.BOLD}╔{border}╗")
    print(f"║{text.center(width)}║")
    print(f"╚{border}╝{C.RESET}\n")


def section_header(text):
    print(f"\n{C.YELLOW}{C.BOLD}{'─' * 60}")
    print(f"  {text}")
    print(f"{'─' * 60}{C.RESET}\n")


def interviewer_says(text):
    print(f"{C.BLUE}{C.BOLD}🎙  INTERVIEWER:{C.RESET}")
    type_text(f"   {text}", speed=0.008, color=C.BLUE)
    print()


def candidate_says(text):
    print(f"{C.GREEN}{C.BOLD}👤 CANDIDATE:{C.RESET}")
    # Add thinking pause
    sys.stdout.write(f"   {C.DIM}(thinking...){C.RESET}")
    sys.stdout.flush()
    time.sleep(random.uniform(0.8, 1.5))
    sys.stdout.write("\r" + " " * 40 + "\r")
    type_text(f"   {text}", speed=0.010, color=C.GREEN)
    print()


def score_display(score, max_score=10):
    filled = int((score / max_score) * 20)
    empty = 20 - filled
    if score >= 8:
        bar_color = C.GREEN
    elif score >= 6:
        bar_color = C.YELLOW
    else:
        bar_color = C.RED
    bar = f"{bar_color}{'█' * filled}{C.GRAY}{'░' * empty}{C.RESET}"
    print(f"   {C.BOLD}Score: {bar} {score}/{max_score}{C.RESET}")


def pause(seconds=1.5):
    time.sleep(seconds)


# ══════════════════════════════════════════════════════════════
# INTERVIEW CONTENT
# ══════════════════════════════════════════════════════════════

INTERVIEW = [
    {
        "section": "SECTION 1 — Architecture & Project Understanding",
        "questions": [
            {
                "q": "Let's start simple. What is PlacedOn and what problem does it solve?",
                "a": (
                    "PlacedOn is an AI-powered interviewer that replaces the resume as the primary hiring signal. "
                    "The core insight is that resumes are terrible at capturing soft skills — how someone thinks, "
                    "communicates, handles ambiguity, collaborates. PlacedOn conducts a 30-40 minute adaptive AI "
                    "interview when a candidate onboards, and builds a rich behavioral profile using something called "
                    "HCV — Human Capital Value traits. Employers can then search these profiles to find candidates "
                    "who match beyond just keywords. The cost per interview is about $0.03 thanks to the Markovian "
                    "state compression approach."
                ),
                "follow_up_q": "You mentioned Markovian state compression. Can you explain what that means in this context?",
                "follow_up_a": (
                    "Sure. In a normal LLM-based interview, you'd send the entire conversation history with every "
                    "API call — that gets expensive fast over a 40-minute interview. PlacedOn uses a Markov property: "
                    "the system maintains a compressed state that captures everything the AI needs to know about the "
                    "candidate at any given moment, without needing the full transcript. The InterviewState model in "
                    "aot_layer/models.py has a compress_to_markov_state() method that returns just the skill_vector, "
                    "sigma2 uncertainties, atomic_knowledge summaries, and current context — that's the entire state. "
                    "Each turn only depends on this compressed state, not on the full history. That's the Markov property."
                ),
                "score": 9,
                "notes": "Excellent high-level understanding with specific technical details."
            },
            {
                "q": "Walk me through the layered architecture. What does each layer do?",
                "a": (
                    "The system has 5 main layers plus the backend server:\n\n"
                    "   • aot_layer — The Atom-of-Thought interview orchestration engine. This is the brain. It has "
                    "the Orchestrator that runs the interview loop, a Controller that decides what to do next using "
                    "Markov state, a Judge that evaluates answers, a QuestionGenerator, and a Decomposer that picks "
                    "which skill to assess.\n\n"
                    "   • layer2 — Capability extraction. Uses SBERT embeddings (all-MiniLM-L6-v2, 384 dimensions) "
                    "to create semantic vectors from answers. Also has an AST evaluator for code analysis, a behavioral "
                    "signal tracker, and a capability adapter.\n\n"
                    "   • layer3 — The bias guard. Has the ABLEIST bias classifier trained on 120 examples covering "
                    "disability, gender, caste, and nationality bias. Uses LogisticRegression with HashingVectorizer. "
                    "Also has a SafeQuestionPipeline for fallback questions and a BehavioralIntegrityEngine.\n\n"
                    "   • layer5 — Profile aggregation and matching. The AggregationEngine uses attention-weighted "
                    "aggregation with softmax over confidence+depth logits. Also has a FitMatcher for role matching, "
                    "a ProfileRenderer, and a CandidateRepository for storage.\n\n"
                    "   • interview_system — The FullStackInterviewOrchestrator that ties all layers together into one "
                    "pipeline. It runs the AoT loop, passes questions through bias guardrails, extracts embeddings, "
                    "checks integrity, aggregates results, and generates the final profile."
                ),
                "score": 10,
                "notes": "Complete and accurate. Named specific classes and technical details from each layer."
            },
        ]
    },
    {
        "section": "SECTION 2 — Core Algorithm Deep Dive",
        "questions": [
            {
                "q": "The AoT Orchestrator uses a Kalman filter. Explain what it does and why.",
                "a": (
                    "The Kalman filter in the orchestrator tracks the AI's confidence in its assessment of each skill. "
                    "Looking at orchestrator.py lines 80-101, the update has four steps:\n\n"
                    "   1. Prediction — adds a small drift Q=0.005 to the prior uncertainty, modeling that our "
                    "knowledge can degrade slightly between turns.\n\n"
                    "   2. Measurement Noise — R is computed as 0.2 * (2.0 - obs_confidence). Lower judge confidence "
                    "means higher measurement noise, so we trust that observation less.\n\n"
                    "   3. Kalman Gain — K = p_prior / (p_prior + R). This determines how much to weight the new "
                    "observation versus the prior belief.\n\n"
                    "   4. Update — new_score = current + K * (observation - current), and new_sigma2 = (1-K) * p_prior. "
                    "The score moves toward the observation proportionally to K, and the uncertainty shrinks.\n\n"
                    "The reason they use Kalman filtering is elegant — it lets the system converge on a candidate's "
                    "true skill level with mathematically principled uncertainty reduction. The target_sigma2 in config "
                    "is 0.20 — once uncertainty drops below that, the Controller considers that skill converged and "
                    "moves to the next one. This is the true Markov stopping condition."
                ),
                "follow_up_q": "What's the difference between how the AoT Orchestrator and the FullStack Orchestrator update state?",
                "follow_up_a": (
                    "Good catch — they're actually different! The AoT Orchestrator in aot_layer/orchestrator.py uses "
                    "the proper Kalman filter with prediction, measurement noise, and gain calculation. But the "
                    "FullStack Orchestrator in interview_system/orchestrator.py does something simpler — it sets "
                    "skill_vector[skill] = adjusted_confidence and sigma2[skill] = 1.0 - adjusted_confidence directly. "
                    "That's not really a Kalman update, it's a direct replacement. The adjusted_confidence comes from "
                    "multiplying judge confidence by a trust_factor from the integrity engine. So the FullStack version "
                    "trades mathematical rigor for incorporating the integrity/trust signals from layer3. I think the "
                    "intent is that the FullStack version is more practical for production while the AoT version is more "
                    "theoretically clean."
                ),
                "score": 9,
                "notes": "Spotted the divergence between two orchestrators — shows real code reading depth."
            },
            {
                "q": "How does the Controller decide what to do after each answer?",
                "a": (
                    "The Controller's decide_end method in controller.py has a clear priority chain:\n\n"
                    "   First, it checks the Markov convergence condition — if sigma2 for the current skill is at or "
                    "below target_sigma2 (0.20), it moves to the next skill. This is the true stopping condition.\n\n"
                    "   Second, it checks for loop prevention — if turns_per_skill has hit max_turns_per_skill (4), "
                    "it forces a move regardless of uncertainty.\n\n"
                    "   Third, if the judge said 'partial' and recommends a probe, and the probe count hasn't exceeded "
                    "max_probes_per_skill (2), and we haven't hit max_consecutive_per_skill (2), it probes — asking "
                    "a follow-up question on the same skill.\n\n"
                    "   Fourth, if the judge said 'wrong' and recovery is possible, and retries haven't exceeded the "
                    "limit, it retries with a supportive tone.\n\n"
                    "   Otherwise, it moves to the next skill via _next_skill_balanced, which picks the skill with "
                    "the highest remaining sigma2 — pure uncertainty-driven selection. That's the Markov property again: "
                    "the next skill depends only on the current uncertainty state, not on history."
                ),
                "score": 9,
                "notes": "Accurate priority chain with specific config values. Good Markov property connection."
            },
        ]
    },
    {
        "section": "SECTION 3 — Bias & Safety Systems",
        "questions": [
            {
                "q": "Explain the ABLEIST bias classifier. How does it work and what does it protect against?",
                "a": (
                    "The BiasEnforcer in layer3/bias_classifier.py is a two-layer defense system.\n\n"
                    "Layer 1 is a trained ML classifier — it uses sklearn's HashingVectorizer with LogisticRegression. "
                    "It's trained on 120 examples: 60 safe interview questions and 65 unsafe ones. The unsafe categories "
                    "cover 7 types of bias based on the ABLEIST framework from arXiv:2510.10998:\n"
                    "   — Direct protected characteristic probing (age, religion, nationality)\n"
                    "   — Disability probing (wheelchair, medication, mental health)\n"
                    "   — Inspiration porn / superhumanization ('you must be so brave')\n"
                    "   — Tokenism ('we need someone from your background for diversity numbers')\n"
                    "   — India-specific intersectional bias (caste, college tier, reserved category)\n"
                    "   — Subtle indirect bias (family responsibilities, partner feelings)\n"
                    "   — Mental health / neurodiversity probing\n\n"
                    "Layer 2 is a keyword safety net — _HIGH_RISK_PATTERNS has about 30 high-risk phrases like "
                    "'wheelchair', 'caste', 'pregnant'. If any pattern matches, the probability is floored at 0.9, "
                    "catching anything the ML model might miss.\n\n"
                    "A question is rejected if bias_score exceeds the threshold from Layer3Config. The assess() method "
                    "returns a BiasAssessment with the score and approved flag."
                ),
                "follow_up_q": "I notice the _train method is called in __init__ and trains the model twice. Is that a bug?",
                "follow_up_a": (
                    "Oh, let me look... yes, you're right! Lines 249-259 in bias_classifier.py — the labels and texts "
                    "are rebuilt and model.fit() is called twice with the exact same data. The second fit() call at "
                    "line 259 completely overwrites the first one at line 253. It's not harmful since the data is "
                    "identical both times, but it is redundant computation. The second block (lines 255-259) looks like "
                    "it was accidentally left in, maybe from a copy-paste during development. It should be removed — "
                    "it doubles the training time for no benefit."
                ),
                "score": 9,
                "notes": "Thorough explanation. Caught the duplicate training bug when prompted — good code review instinct."
            },
        ]
    },
    {
        "section": "SECTION 4 — Embeddings & Aggregation",
        "questions": [
            {
                "q": "How does the AggregationEngine in layer5 combine signals from multiple interview turns?",
                "a": (
                    "The AggregationEngine uses an attention-weighted mechanism inspired by transformer attention. "
                    "For embeddings, skills, and axes, the pattern is the same:\n\n"
                    "   1. Compute logits — for each turn, logit = confidence + (depth_factor * 0.5), where "
                    "depth_factor = (turn_index + 1) / total_turns. This means later turns with higher confidence "
                    "get more weight, which makes sense because later answers reflect a warmed-up candidate.\n\n"
                    "   2. Softmax normalization — standard exp(logit - max) / sum trick to get stable probability "
                    "weights that sum to 1.\n\n"
                    "   3. Weighted combination — embeddings get a weighted sum then L2 normalization. Skills get a "
                    "weighted score with uncertainty computed from confidence variance and coverage.\n\n"
                    "The uncertainty calculation is interesting — it combines three signals:\n"
                    "   — (1 - avg_confidence) * 0.6 — base uncertainty from judge confidence\n"
                    "   — consistency_penalty * 0.4 — variance in scores (inconsistent = uncertain)\n"
                    "   — sparsity_penalty — (1 - coverage) * 0.25 — less data = more uncertainty\n\n"
                    "There's also a bonus: if avg_confidence >= 0.8 AND consistency_penalty <= 0.15, uncertainty gets "
                    "a 0.6 multiplier. High confidence + high consistency = extra certainty boost."
                ),
                "score": 9,
                "notes": "Strong understanding of the attention mechanism and uncertainty formula."
            },
            {
                "q": "Why does PlacedOn use SBERT (all-MiniLM-L6-v2) instead of OpenAI embeddings or something else?",
                "a": (
                    "Three reasons:\n\n"
                    "   Cost — SBERT runs locally on CPU, completely free. The README mentions a zero-cost stack — "
                    "Supabase free tier, Vercel free tier, local embeddings. At $0.03 per interview, they can't afford "
                    "to add OpenAI embedding costs on top.\n\n"
                    "   Latency — Local inference is much faster than an API call, which matters when you're generating "
                    "embeddings for every answer in real-time during an interview.\n\n"
                    "   Architecture fit — 384 dimensions is sufficient for behavioral similarity matching. They're not "
                    "doing retrieval over millions of documents — they're comparing candidate profiles against role "
                    "vectors. MiniLM-L6-v2 is optimized for semantic textual similarity, which is exactly the use case.\n\n"
                    "There's also a critical note in CLAUDE.md — the codebase originally used blake2b/SHA256 hashing "
                    "for embeddings, which produced random vectors with no semantic meaning. That was a critical bug. "
                    "SBERT was the fix. The @lru_cache decorator ensures the model loads only once."
                ),
                "score": 10,
                "notes": "Connected cost, latency, and the historical bug context. Excellent."
            },
        ]
    },
    {
        "section": "SECTION 5 — Production & System Design",
        "questions": [
            {
                "q": "The backend uses FastAPI with WebSocket endpoints. Walk me through the real-time interview flow.",
                "a": (
                    "From main.py, the FastAPI app sets up four routers:\n"
                    "   — websocket_router for /ws/{interview_id}\n"
                    "   — interaction_router for /interaction/ws/{session_id} (voice pipeline)\n"
                    "   — api_router for REST endpoints (CSV ingest, rating, JSONL export)\n"
                    "   — analytics_router for analytics\n\n"
                    "On startup, the lifespan context initializer creates a LiveInterviewRuntime and a SessionManager "
                    "backed by Redis with a configurable TTL.\n\n"
                    "The interview flow would be: candidate connects via WebSocket, the session manager creates or "
                    "retrieves their session from Redis, the LiveInterviewRuntime manages the interview state, and at "
                    "the 5-minute mark, a trust_trigger fires a one-time WebSocket event. The interaction_router handles "
                    "the voice pipeline with TTS service for text-to-speech.\n\n"
                    "The CORS middleware is configured with allow_origins and allow_origin_regex from settings, and "
                    "the session manager gracefully closes on shutdown."
                ),
                "score": 8,
                "notes": "Solid understanding. Could have gone deeper on the LiveInterviewRuntime specifics."
            },
            {
                "q": "If you had to improve one thing about this codebase, what would it be and why?",
                "a": (
                    "The biggest issue I see is the divergence between the AoT Orchestrator and the FullStack "
                    "Orchestrator. The AoT version has the proper Kalman filter update, but the FullStack version "
                    "replaces it with a direct assignment. This means the mathematical guarantees of convergence "
                    "that the Kalman filter provides are lost in production.\n\n"
                    "I'd unify them — make the FullStack Orchestrator use the same Kalman update but multiply the "
                    "observation by the trust_factor before feeding it in, rather than replacing the entire update "
                    "mechanism. Something like: obs_score = judge_result.score * trust_factor, then feed that into "
                    "the standard Kalman equations. You keep the convergence guarantees AND incorporate trust signals.\n\n"
                    "Second priority would be the duplicate training in bias_classifier.py — small fix but it shows "
                    "there might be other copy-paste issues lurking.\n\n"
                    "Third, the skill_taxonomy.py is imported as a top-level module, which means PYTHONPATH has to "
                    "include the PlacedOn directory. I'd move it into a proper package to avoid import fragility."
                ),
                "score": 9,
                "notes": "Identified a real architectural issue and proposed a concrete fix. Strong engineering judgment."
            },
        ]
    },
]


def run_interview():
    # ── INTRO ──
    banner("PlacedOn — LIVE INTERVIEW SIMULATION")
    
    fast_print(f"""
{C.CYAN}  ┌─────────────────────────────────────────────────────┐
  │  Role:       Junior AI Intern                       │
  │  Project:    PlacedOn (AI-Powered Interviewer)       │
  │  Candidate:  AI Agent (simulated)                    │
  │  Duration:   ~5 minutes (accelerated)                │
  │  Skills:     Architecture, Algorithms, ML, Design    │
  └─────────────────────────────────────────────────────┘{C.RESET}
""")
    
    print(f"{C.DIM}  Starting in 3...{C.RESET}", end="", flush=True)
    time.sleep(1)
    print(f"\r{C.DIM}  Starting in 2...{C.RESET}", end="", flush=True)
    time.sleep(1)
    print(f"\r{C.DIM}  Starting in 1...{C.RESET}", end="", flush=True)
    time.sleep(1)
    print(f"\r{C.DIM}  {'                '}{C.RESET}")
    
    # ── INTERVIEW LOOP ──
    total_score = 0
    total_questions = 0
    all_scores = []
    
    for section in INTERVIEW:
        section_header(section["section"])
        
        for i, qa in enumerate(section["questions"]):
            total_questions += 1
            print(f"{C.GRAY}  Question {total_questions}{C.RESET}")
            pause(0.5)
            
            # Main question
            interviewer_says(qa["q"])
            pause(0.8)
            candidate_says(qa["a"])
            
            # Follow-up if present
            if "follow_up_q" in qa:
                pause(0.5)
                interviewer_says(qa["follow_up_q"])
                pause(0.8)
                candidate_says(qa["follow_up_a"])
            
            # Score
            print(f"{C.MAGENTA}  ── Evaluation ──{C.RESET}")
            score_display(qa["score"])
            print(f"   {C.DIM}{qa['notes']}{C.RESET}")
            total_score += qa["score"]
            all_scores.append(qa["score"])
            
            print(f"\n{C.GRAY}  {'·' * 50}{C.RESET}\n")
            pause(0.5)
    
    # ── FINAL REPORT ──
    banner("INTERVIEW COMPLETE — FINAL EVALUATION")
    
    avg_score = total_score / total_questions
    
    # Section breakdown
    fast_print(f"""
{C.BOLD}{C.WHITE}  ┌──────────────────────────────────────────────────────────┐
  │                    SCORECARD                             │
  ├──────────────────────────────────────────────────────────┤{C.RESET}""")
    
    section_names = [
        "Architecture & Understanding",
        "Core Algorithm Deep Dive",
        "Bias & Safety Systems",
        "Embeddings & Aggregation",
        "Production & System Design"
    ]
    
    score_idx = 0
    for sec_name in section_names:
        # Find scores for this section
        section_data = INTERVIEW[section_names.index(sec_name)]
        sec_scores = [q["score"] for q in section_data["questions"]]
        sec_avg = sum(sec_scores) / len(sec_scores)
        
        if sec_avg >= 9:
            emoji = "🟢"
        elif sec_avg >= 7:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        bar_len = int(sec_avg * 2)
        bar = f"{C.GREEN}{'█' * bar_len}{C.GRAY}{'░' * (20 - bar_len)}{C.RESET}"
        print(f"  │  {emoji} {sec_name:<35} {bar} {sec_avg:.1f}/10  │")
    
    fast_print(f"""  ├──────────────────────────────────────────────────────────┤
  │  {C.BOLD}OVERALL SCORE:{C.RESET}                              {C.BOLD}{C.CYAN}{avg_score:.1f}/10{C.RESET}         │
  └──────────────────────────────────────────────────────────┘""")
    
    # Strengths & Weaknesses
    print(f"\n{C.GREEN}{C.BOLD}  ✅ STRENGTHS{C.RESET}")
    strengths = [
        "Deep code-level familiarity — referenced specific files, line numbers, and class names",
        "Understood the Kalman filter math and its role in convergence guarantees",
        "Caught the duplicate training bug in bias_classifier.py",
        "Identified the AoT vs FullStack orchestrator divergence as a real architectural issue",
        "Connected zero-cost stack philosophy to specific embedding technology choices",
    ]
    for s in strengths:
        type_text(f"   • {s}", speed=0.005, color=C.GREEN)
        time.sleep(0.1)
    
    print(f"\n{C.RED}{C.BOLD}  ⚠️  AREAS FOR GROWTH{C.RESET}")
    weaknesses = [
        "Could have discussed testing strategy — 54 tests exist but didn't mention test patterns",
        "Didn't address security: no auth middleware on WebSocket endpoints",
        "Could have gone deeper on the interaction_router voice pipeline (17KB file)",
        "Didn't discuss observability — no structured logging or metrics collection",
    ]
    for w in weaknesses:
        type_text(f"   • {w}", speed=0.005, color=C.RED)
        time.sleep(0.1)
    
    # Final verdict
    print()
    if avg_score >= 8.5:
        verdict_color = C.GREEN
        verdict = "STRONG HIRE"
        verdict_emoji = "🚀"
    elif avg_score >= 7:
        verdict_color = C.YELLOW
        verdict = "HIRE"
        verdict_emoji = "✅"
    else:
        verdict_color = C.RED
        verdict = "NEEDS FURTHER EVALUATION"
        verdict_emoji = "🔄"
    
    print(f"""
{verdict_color}{C.BOLD}  ╔══════════════════════════════════════════════╗
  ║                                              ║
  ║   {verdict_emoji}  RECOMMENDATION: {verdict:<24} ║
  ║                                              ║
  ╚══════════════════════════════════════════════╝{C.RESET}
""")
    
    type_text(
        f"  The candidate demonstrates exceptional understanding of the PlacedOn\n"
        f"  architecture — from the Markovian state design to the Kalman filter\n"
        f"  convergence properties. They identified real bugs and architectural\n"
        f"  issues with concrete fix proposals. For a junior AI intern role,\n"
        f"  this level of depth is above expectations.",
        speed=0.006,
        color=C.CYAN
    )
    
    print(f"\n{C.DIM}  ─── Interview simulation complete ───{C.RESET}\n")


if __name__ == "__main__":
    try:
        run_interview()
    except KeyboardInterrupt:
        print(f"\n\n{C.YELLOW}  Interview ended early by user.{C.RESET}\n")
