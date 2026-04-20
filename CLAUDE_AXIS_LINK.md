# 🛡️ CLAUDE AXIS DIRECT ACCESS MAPPING
> **System Interpretability Index:**
> Use this file to navigate the 10-Axis Evaluation framework within the PlacedOn reactor.

## 📊 The 10-Axis Model

### 1. Behavioral Core (Psychometrics)
- **Ax-1: Grit & Follow-through** — Resilience vs. stopping power.
- **Ax-2: Stress Resilience** — Regulatory capacity under high-stakes simulation.
- **Ax-3: Collaboration / Social** — Alignment and stakeholder empathy metrics.

### 2. Operational Mastery (Execution)
- **Ax-4: Ownership** — Proactive error correction and accountability.
- **Ax-5: Curiosity / Learning Agility** — Information-seeking depth.
- **Ax-6: Self-Awareness / Calibration** — Uncertainty mapping (Sigma-2 alignment).

### 3. Technical & Logic (Reasoning)
- **Ax-7: Technical Depth & Mechanism** — Tool-specific mechanical knowledge.
- **Ax-8: Trade-off Reasoning** — System design and constraint navigation.

### 4. Safety & Integrity (Claude-Specific)
- **Ax-9: Communication Nuance** — Tone, clarity, and non-hallucinated evidence.
- **Ax-10: Integrity & Bias Safety** — ABLEIST constraint enforcement.

---

## 🔗 Implementation Linkage

- **Evaluator Logic:** `PlacedOn/backend/llm/claude_axis.py` [NEW]
- **Aggregation Engine:** `PlacedOn/layer5/aggregator.py` [UPDATE]
- **Signal Models:** `PlacedOn/layer5/models.py` [UPDATE]
- **Verification Loop:** `PlacedOn/training/train_pipeline.py` [UPDATE]

## 🛠️ Direct Commands
*   **Run Axis Validation Suite:**
    `PYTHONPATH=PlacedOn:PlacedOn/backend pytest PlacedOn/tests/test_claude_axis.py`
*   **Generate Axis Radar Profile:**
    `python3 PlacedOn/simulate_interview.py --axis-mode`
