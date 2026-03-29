# Layer 5: Persistent Storage & Output

Layer 5 finalizes interview signals into a durable candidate representation, computes similarity-based fit, and renders evidence-grounded outputs.

## What this layer does

1. Aggregates multi-turn interview signals:
   - confidence-weighted and recency-weighted skill scores
   - embedding aggregation across turns
   - L2-normalized final embedding
   - uncertainty modeling that reflects consistency and observation coverage
2. Stores candidate state in an async repository:
   - pgvector-compatible simulated adapter
   - in-memory backend for local testing
3. Computes fit using embedding cosine similarity only:
   - no hardcoded embedding dimensions
   - qualitative interpretation (`low`, `medium`, `high alignment`)
4. Renders employer-readable profile output:
   - traits strictly tied to evidence
   - no hallucinated traits when evidence is missing
   - confidence notes include uncertainty

## Project structure

```text
layer5/
├── __init__.py
├── aggregator.py
├── config.py
├── main.py
├── matcher.py
├── models.py
├── renderer.py
├── storage.py
├── tests/
│   ├── test_aggregation.py
│   ├── test_matching.py
│   └── test_renderer.py
└── README.md
```

## Data model highlights

- Embeddings are `list[float]` with no fixed dimension.
- All cosine operations verify dimensional consistency at runtime.
- Candidate state stores:
  - `candidate_id`
  - aggregated `embedding`
  - `skills` with `score`, `uncertainty`, and `evidence`
  - metadata

## Manual demo

From repo root:

```bash
python3 layer5/main.py
```

Expected output includes logs like:

```text
[Aggregation] Final vector computed
[Matcher] Fit score: 0.xx
[Renderer] Generated traits with evidence
```

## Tests

Run:

```bash
python3 -m pytest -q layer5/tests
```

Current expected result:

- `11 passed`

## Test coverage summary

### Aggregation
- Multi-turn weighted aggregation works
- Higher confidence/recency has higher impact
- Embedding is normalized
- Uncertainty decreases for consistent strong signals
- Incomplete/missing skill data handled

### Matching
- Identical embeddings -> high similarity
- Different embeddings -> lower similarity
- Interpretation remains qualitative (no exact % claim)

### Renderer
- Traits always tied to evidence
- No trait generated from missing evidence
- Uncertainty reflected in confidence notes
- Low-confidence signals reduce trait output

## pgvector note

`PgVectorStorageAdapter` is implemented as a simulation wrapper so local execution and tests are dependency-light.

For production, replace adapter internals with actual PostgreSQL + pgvector operations (e.g. asyncpg/SQLAlchemy) while keeping the same repository interface.
