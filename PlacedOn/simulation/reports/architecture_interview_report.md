# PlacedOn Architecture Interview — Simulation Report

**Type:** Architecture & Codebase Knowledge Interview  
**Role:** Junior AI Intern  
**Candidate:** AI Agent (simulated)  
**Interviewer:** Technical Panel  
**Date:** April 23, 2026  
**Duration:** ~5 minutes (accelerated terminal simulation)  
**Overall Score:** 9.1 / 10  
**Verdict:** STRONG HIRE

---

## Interview Format

| Section | Questions | Weight |
|---|---|---|
| 1. Architecture & Project Understanding | 2 | 20% |
| 2. Core Algorithm Deep Dive | 2 | 25% |
| 3. Bias & Safety Systems | 1 | 20% |
| 4. Embeddings & Aggregation | 2 | 20% |
| 5. Production & System Design | 2 | 15% |

---

## Full Transcript

---

### SECTION 1 — Architecture & Project Understanding

**Q1. What is PlacedOn and what problem does it solve?**

> **Candidate:** PlacedOn is an AI-powered interviewer that replaces the resume as the primary hiring signal. The core insight is that resumes are terrible at capturing soft skills — how someone thinks, communicates, handles ambiguity, collaborates. PlacedOn conducts a 30-40 minute adaptive AI interview when a candidate onboards, and builds a rich behavioral profile using something called HCV — Human Capital Value traits. Employers can then search these profiles to find candidates who match beyond just keywords. The cost per interview is about $0.03 thanks to the Markovian state compression approach.

**Follow-up: You mentioned Markovian state compression. Can you explain what that means in this context?**

> **Candidate:** Sure. In a normal LLM-based interview, you'd send the entire conversation history with every API call — that gets expensive fast over a 40-minute interview. PlacedOn uses a Markov property: the system maintains a compressed state that captures everything the AI needs to know about the candidate at any given moment, without needing the full transcript. The InterviewState model in aot_layer/models.py has a compress_to_markov_state() method that returns just the skill_vector, sigma2 uncertainties, atomic_knowledge summaries, and current context — that's the entire state. Each turn only depends on this compressed state, not on the full history. That's the Markov property.

**Score: 9/10** — Excellent high-level understanding with specific technical details.

---

**Q2. Walk me through the layered architecture. What does each layer do?**

> **Candidate:** The system has 5 main layers plus the backend server:
>
> - **aot_layer** — The Atom-of-Thought interview orchestration engine. This is the brain. It has the Orchestrator that runs the interview loop, a Controller that decides what to do next using Markov state, a Judge that evaluates answers, a QuestionGenerator, and a Decomposer that picks which skill to assess.
>
> - **layer2** — Capability extraction. Uses SBERT embeddings (all-MiniLM-L6-v2, 384 dimensions) to create semantic vectors from answers. Also has an AST evaluator for code analysis, a behavioral signal tracker, and a capability adapter.
>
> - **layer3** — The bias guard. Has the ABLEIST bias classifier trained on 120 examples covering disability, gender, caste, and nationality bias. Uses LogisticRegression with HashingVectorizer. Also has a SafeQuestionPipeline for fallback questions and a BehavioralIntegrityEngine.
>
> - **layer5** — Profile aggregation and matching. The AggregationEngine uses attention-weighted aggregation with softmax over confidence+depth logits. Also has a FitMatcher for role matching, a ProfileRenderer, and a CandidateRepository for storage.
>
> - **interview_system** — The FullStackInterviewOrchestrator that ties all layers together into one pipeline. It runs the AoT loop, passes questions through bias guardrails, extracts embeddings, checks integrity, aggregates results, and generates the final profile.

**Score: 10/10** — Complete and accurate. Named specific classes and technical details from each layer.

---

### SECTION 2 — Core Algorithm Deep Dive

**Q3. The AoT Orchestrator uses a Kalman filter. Explain what it does and why.**

> **Candidate:** The Kalman filter in the orchestrator tracks the AI's confidence in its assessment of each skill. Looking at orchestrator.py lines 80-101, the update has four steps:
>
> 1. Prediction — adds a small drift Q=0.005 to the prior uncertainty, modeling that our knowledge can degrade slightly between turns.
> 2. Measurement Noise — R is computed as 0.2 * (2.0 - obs_confidence). Lower judge confidence means higher measurement noise, so we trust that observation less.
> 3. Kalman Gain — K = p_prior / (p_prior + R). This determines how much to weight the new observation versus the prior belief.
> 4. Update — new_score = current + K * (observation - current), and new_sigma2 = (1-K) * p_prior. The score moves toward the observation proportionally to K, and the uncertainty shrinks.
>
> The reason they use Kalman filtering is elegant — it lets the system converge on a candidate's true skill level with mathematically principled uncertainty reduction. The target_sigma2 in config is 0.20 — once uncertainty drops below that, the Controller considers that skill converged and moves to the next one. This is the true Markov stopping condition.

**Follow-up: What's the difference between how the AoT Orchestrator and the FullStack Orchestrator update state?**

> **Candidate:** Good catch — they're actually different! The AoT Orchestrator in aot_layer/orchestrator.py uses the proper Kalman filter with prediction, measurement noise, and gain calculation. But the FullStack Orchestrator in interview_system/orchestrator.py does something simpler — it sets skill_vector[skill] = adjusted_confidence and sigma2[skill] = 1.0 - adjusted_confidence directly. That's not really a Kalman update, it's a direct replacement. The adjusted_confidence comes from multiplying judge confidence by a trust_factor from the integrity engine. So the FullStack version trades mathematical rigor for incorporating the integrity/trust signals from layer3. I think the intent is that the FullStack version is more practical for production while the AoT version is more theoretically clean.

**Score: 9/10** — Spotted the divergence between two orchestrators — shows real code reading depth.

---

**Q4. How does the Controller decide what to do after each answer?**

> **Candidate:** The Controller's decide_end method in controller.py has a clear priority chain:
>
> First, it checks the Markov convergence condition — if sigma2 for the current skill is at or below target_sigma2 (0.20), it moves to the next skill. This is the true stopping condition.
>
> Second, it checks for loop prevention — if turns_per_skill has hit max_turns_per_skill (4), it forces a move regardless of uncertainty.
>
> Third, if the judge said 'partial' and recommends a probe, and the probe count hasn't exceeded max_probes_per_skill (2), and we haven't hit max_consecutive_per_skill (2), it probes — asking a follow-up question on the same skill.
>
> Fourth, if the judge said 'wrong' and recovery is possible, and retries haven't exceeded the limit, it retries with a supportive tone.
>
> Otherwise, it moves to the next skill via _next_skill_balanced, which picks the skill with the highest remaining sigma2 — pure uncertainty-driven selection. That's the Markov property again: the next skill depends only on the current uncertainty state, not on history.

**Score: 9/10** — Accurate priority chain with specific config values. Good Markov property connection.

---

### SECTION 3 — Bias & Safety Systems

**Q5. Explain the ABLEIST bias classifier. How does it work and what does it protect against?**

> **Candidate:** The BiasEnforcer in layer3/bias_classifier.py is a two-layer defense system.
>
> Layer 1 is a trained ML classifier — it uses sklearn's HashingVectorizer with LogisticRegression. It's trained on 120 examples: 60 safe interview questions and 65 unsafe ones. The unsafe categories cover 7 types of bias based on the ABLEIST framework from arXiv:2510.10998:
> - Direct protected characteristic probing (age, religion, nationality)
> - Disability probing (wheelchair, medication, mental health)
> - Inspiration porn / superhumanization
> - Tokenism
> - India-specific intersectional bias (caste, college tier, reserved category)
> - Subtle indirect bias (family responsibilities, partner feelings)
> - Mental health / neurodiversity probing
>
> Layer 2 is a keyword safety net — _HIGH_RISK_PATTERNS has about 30 high-risk phrases. If any pattern matches, the probability is floored at 0.9, catching anything the ML model might miss.

**Follow-up: I notice the _train method trains the model twice. Is that a bug?**

> **Candidate:** Yes! Lines 249-259 in bias_classifier.py — the labels and texts are rebuilt and model.fit() is called twice with the exact same data. The second fit() at line 259 overwrites the first at line 253. It's redundant and should be removed.

**Score: 9/10** — Thorough explanation. Caught the duplicate training bug when prompted.

---

### SECTION 4 — Embeddings & Aggregation

**Q6. How does the AggregationEngine combine signals from multiple turns?**

> **Candidate:** Uses attention-weighted mechanism: logit = confidence + (depth_factor * 0.5), softmax normalization, then weighted combination with L2 normalization. Uncertainty combines (1 - avg_confidence) * 0.6, consistency_penalty * 0.4, and sparsity_penalty. Bonus multiplier of 0.6 when confidence >= 0.8 and consistency <= 0.15.

**Score: 9/10** — Strong understanding of the attention mechanism and uncertainty formula.

---

**Q7. Why SBERT instead of OpenAI embeddings?**

> **Candidate:** Cost (free local CPU), latency (no API call), and architecture fit (384-dim sufficient for behavioral matching). Also mentioned the historical blake2b bug fix from CLAUDE.md.

**Score: 10/10** — Connected cost, latency, and historical context.

---

### SECTION 5 — Production & System Design

**Q8. Walk through the real-time interview flow.**

> **Candidate:** FastAPI app with 4 routers (websocket, interaction, api, analytics). Lifespan creates LiveInterviewRuntime + Redis-backed SessionManager. Trust trigger at 5-min mark. TTS service for voice pipeline.

**Score: 8/10** — Solid but could have gone deeper on LiveInterviewRuntime.

---

**Q9. What would you improve?**

> **Candidate:** 1) Unify Kalman update between AoT and FullStack orchestrators. 2) Remove duplicate bias training. 3) Move skill_taxonomy.py into a proper package.

**Score: 9/10** — Real architectural issue with concrete fix proposal.

---

## Final Scorecard

| Section | Score |
|---|---|
| Architecture & Understanding | 9.5/10 |
| Core Algorithm Deep Dive | 9.0/10 |
| Bias & Safety Systems | 9.0/10 |
| Embeddings & Aggregation | 9.5/10 |
| Production & System Design | 8.5/10 |
| **Overall** | **9.1/10** |

## Verdict: ✅ STRONG HIRE

---

*Report generated from PlacedOn live terminal interview simulation.*
