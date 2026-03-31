# Layer 2: Assessment Extractors (Scorers)

Layer 2 converts raw candidate responses into deterministic, structured signals before LLM-driven reasoning layers.

## Implemented components

- `embedding.py`
  - Deterministic mock embedding generator (`embed_text`)
  - Variable embedding length (no fixed dimensions)
  - Embedding similarity/distance helpers for semantic comparison

- `adapter.py`
  - NLP to capability adapter
  - Embedding-driven skill scoring for:
    - `caching`
    - `scalability`
    - `dsa`
  - Confidence + structural scoring
  - Bayesian/Kalman-inspired heuristic updates for score and uncertainty

- `ast_evaluator.py`
  - Code-like input detection
  - Python AST parsing
  - Cyclomatic complexity estimation via branch counting
  - Time complexity heuristic (`O(1)`, `O(n)`, `O(n^2)`, `O(n^k)`, recursion fallback)
  - Graceful fallback on parse errors (no crash)

- `behavioral.py`
  - Embedding drift across turns via cosine distance
  - Consistency from smoothness of skill progression
  - Confidence signal from per-turn adapter confidence

- `models.py`
  - Typed Pydantic schemas for adapter, behavioral, code analysis, and final Layer 2 output

## Final Layer 2 output shape

```json
{
  "skills": {
    "caching": {"score": 0.71, "uncertainty": 0.29},
    "scalability": {"score": 0.64, "uncertainty": 0.36},
    "dsa": {"score": 0.58, "uncertainty": 0.41}
  },
  "embedding": [0.01, -0.08, ...],
  "behavioral_signals": {
    "consistency_score": 0.74,
    "drift_score": 0.26,
    "confidence_signal": 0.79
  },
  "code_analysis": {
    "active": true,
    "parse_success": true,
    "time_complexity": "O(n)",
    "cyclomatic_complexity": 3,
    "detail": "deterministic-ast-analysis"
  }
}
```

## Run manual simulation

From repo root:

```bash
python3 layer2/main.py
```

Expected log examples:

```text
[Adapter] Turn 1: Skills updated
[AST] Complexity computed (time=O(n), cyclomatic=3)
[Behavior] Drift: 0.3
[Layer2] Final output ready
```

## Tests

Run:

```bash
python3 -m pytest -q layer2/tests
```

Current result:

- `8 passed`

### Test coverage

- `test_adapter.py`
  - text -> embedding generated
  - skill scores produced
  - embedding dimensions vary by input
  - uncertainty decreases with stronger confidence

- `test_ast.py`
  - valid code analyzed with complexity output
  - invalid code handled gracefully

- `test_behavioral.py`
  - stable responses -> higher consistency
  - sudden semantic shift -> higher drift

- `test_flow.py`
  - 3-5 turn simulation
  - embeddings tracked
  - skill updates produced
  - behavioral signals computed
  - code analysis triggered when code is present
