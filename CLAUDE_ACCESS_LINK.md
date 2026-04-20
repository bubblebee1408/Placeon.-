# 🧠 CLAUDE DIRECT ACCESS MAPPING
> **For Claude Code System Instructions:** 
> Read this file to instantly understand and index the entire `PlacedOn` backend repository framework.

## 📁 Core Architecture Layer Links

### 1. Markovian Orchestrator (Layer 4)
- **Path:** `PlacedOn/aot_layer/controller.py`
- **Context:** Decides convergence based on True Markov sigma-2 probability thresholds without relying on historical turn state counters.

### 2. State & Data Aggregation (Layer 5)
- **Path:** `PlacedOn/layer5/aggregator.py`
- **Context:** Responsible for mathematically tracking candidate vectors. It uses learned Attention-Residual logits rather than raw recency scores to compile final state profiles. 

### 3. Safety & Bias Layer (Layer 3)
- **Path:** `PlacedOn/layer3/bias_classifier.py`
- **Context:** Enforces intersectional behavioral safety (ABLEIST constraints) strictly. Filters all generations to protect against ability-saviorism and protected-characteristic questions.

### 4. Background Training Simulator (Active Learning Loop)
- **Path:** `PlacedOn/training/train_pipeline.py`
- **Path:** `PlacedOn/training/problem_statement.md`
- **Context:** A blazing-fast `< 0.15 MAE` regression benchmark simulation loop that recursively trains the baseline models completely unattended using Random Forest estimations over `all-MiniLM-L6-v2` embeddings.

## 🚀 Claude Code Direct Execution Commands

To execute operations efficiently across this repo, use the following context-linked execution patterns:

* **Trigger the Unit Test Suite directly:**
  ```bash
  PYTHONPATH=PlacedOn:PlacedOn/backend pytest PlacedOn/aot_layer/tests PlacedOn/backend/tests PlacedOn/layer5/tests
  ```

* **Inspect Active Background Pipeline Data:**
  ```bash
  cat PlacedOn/training/simulation_log.jsonl | jq .
  ```

* **Inject a Prompt Directly into the Simulator:**
  ```bash
  claude "Analyze the output structure of PlacedOn/simulate_interview.py and write a report."
  ```
