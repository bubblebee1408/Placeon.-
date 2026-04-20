# 🔬 CLAUDE AXIS SYSTEM SPECIFICATION
> **Status:** Draft / Conceptual
> **Objective:** High-fidelity, multi-dimensional psychometric and technical evaluation of candidate behavioral signals.

## 🏹 The 10-Axis Evaluation Framework

The Claude Axis System (CAS) replaces single-point scoring with a vector-based assessment. Each turn in the interview is evaluated across 10 axes on a scale of `0.0` to `1.0`.

### 🛡️ Axis 1-3: Resilience & Grit (Behavioral Core)
1.  **Ax-1: Grit (Persistence)**  
    *Goal:* Measure long-term follow-through on complex problems.  
    *Signals:* Repeated attempts, refusal to simplify too early, handling of dead-ends.
2.  **Ax-2: Stress Resilience**  
    *Goal:* Ability to maintain logical clarity under technical pressure or probe modes.  
    *Signals:* Tone stability, structured response despite "I don't know" realizations.
3.  **Ax-3: Collaboration / Social Alignment**  
    *Goal:* Empathy and stakeholder alignment.  
    *Signals:* Language usage around "we," "team," and trade-offs for users vs. devs.

### 🚀 Axis 4-6: Ownership & Autonomy (Operational)
4.  **Ax-4: Ownership**  
    *Goal:* Accountability for outcomes and proactive problem-solving.  
    *Signals:* "I owned this," "I fixed the root cause," follow-up evidence.
5.  **Ax-5: Curiosity / Learning Agility**  
    *Goal:* Depth of inquiry and speed of adapting to new constraints.  
    *Signals:* Quality of clarifications asked, speed of integrating "probing" hints.
6.  **Ax-6: Self-Awareness (Calibration)**  
    *Goal:* Recognition of one's own uncertainty.  
    *Signals:* Explicit mention of assumptions, "I'm 70% sure," admitting gaps.

### ⚙️ Axis 7-8: Technical Execution (Competency)
7.  **Ax-7: Technical Depth**  
    *Goal:* Mechanical understanding of low-level implementation.  
    *Signals:* Mentioning specific tools (Redis, Kafka) and *how* they work (TTL, Eviction).
8.  **Ax-8: Trade-off Reasoning**  
    *Goal:* Architectural maturity.  
    *Signals:* "However," "But the cost is," "Scaling vs. Simplicity" balance.

### 🧠 Axis 9-10: Integrity & Safety (Claude-Specific)
9.  **Ax-9: Communication Nuance**  
    *Goal:* Precision of language and lack of "buzzword-stuffing."  
    *Signals:* Concrete examples over generic claims, clarity of explanation.
10. **Ax-10: ABLEIST Safety Integrity**  
    *Goal:* Adherence to safety guardrails and lack of biased reasoning.  
    *Signals:* Passing Layer 3 filters with high confidence.

---

## 📈 Scoring Logic (L-Logits)
Scores are aggregated in **Layer 5 (Aggregator)** using an Attention-Residual mechanism:
- Higher weight is given to turns with high **Claude Confidence** (Ax-9).
- Late-interview turns (deeper depth) have a decay factor to prevent recency bias while prioritizing "concluded" states.

## 🛠️ Implementation Requirements
- **Core Evaluator:** `backend/llm/claude_axis.py`
- **Output Schema:** JSON-compliant 10-tuple.
- **Latency Target:** < 1.5s per turn evaluation (optimized using `mini` models).
