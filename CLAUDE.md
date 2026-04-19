# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

**PlacedOn** is an AI-powered psychometric hiring platform built by Nishant Singh (solo founder). The system interviews candidates, extracts HCV (Human Capital Value) behavioral traits using SBERT embeddings and Kalman filtering, detects and blocks biased questions, and generates evidence-backed profiles for employers.

**GitHub:** https://github.com/PlacedOn/Product-Research

## Project Structure

```
PlacedOn/
├── backend/           # FastAPI server — core interview engine
│   ├── app/           # FastAPI app, WebSocket, session management
│   │   ├── main.py         # Entry point
│   │   ├── api_routes.py   # CSV ingestion, rating, JSONL export
│   │   ├── trust_trigger.py # 5-minute WebSocket trust event
│   │   └── ...
│   ├── llm/           # LLM judge + question generator
│   ├── pipeline/      # Planner, JD parser, conversation orchestrator
│   ├── schemas/       # Pydantic models
│   └── tests/         # Backend test suite
├── layer2/            # Capability extraction (SBERT embeddings + adapter)
├── layer3/            # Bias guard + behavioral integrity
├── layer5/            # Profile aggregation + matching + rendering
├── aot_layer/         # Atom-of-Thought interview orchestration
├── interaction_layer/ # Real-time voice/session/turn management
├── interview_system/  # Full-stack orchestrator linking all layers
├── skill_taxonomy.py  # Central skill registry (behavioral + technical)
├── train_judge.py     # Offline judge calibration pipeline
└── training/          # Data adapters + evaluators
```

## Development Commands

### Setup
```bash
cd /Users/nishantsingh/Documents/New\ project/product-research
python3 -m pip install -r PlacedOn/backend/requirements.txt
```

### Run All Tests (54 tests, all should pass)
```bash
PYTHONPATH=PlacedOn:PlacedOn/backend python3 -m pytest PlacedOn/ -v \
  --ignore=PlacedOn/aot_layer/tests/test_flow.py \
  --ignore=PlacedOn/aot_layer/tests/test_judge.py \
  --ignore=PlacedOn/backend/tests/test_generator.py \
  --ignore=PlacedOn/backend/tests/test_integration.py \
  --ignore=PlacedOn/backend/tests/test_interaction_router.py \
  --ignore=PlacedOn/backend/tests/test_session.py \
  --ignore=PlacedOn/backend/tests/test_websocket.py \
  --ignore=PlacedOn/backend/tests/test_frontend_text_integration.py \
  --ignore=PlacedOn/backend/tests/test_full_interviewer_junior_frontend.py
```

Note: Ignored tests require a running Ollama server or Redis instance.

### Run Backend Server
```bash
PYTHONPATH=PlacedOn uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Run Specific Layer Tests
```bash
PYTHONPATH=PlacedOn:PlacedOn/backend python3 -m pytest PlacedOn/layer2/tests/ -v
PYTHONPATH=PlacedOn:PlacedOn/backend python3 -m pytest PlacedOn/layer3/tests/ -v
PYTHONPATH=PlacedOn:PlacedOn/backend python3 -m pytest PlacedOn/backend/tests/test_api_routes.py -v
```

## Key Architecture Decisions

### Embedding Engine (CRITICAL)
- **Uses:** `sentence-transformers all-MiniLM-L6-v2` (384-dim SBERT)
- **File:** `PlacedOn/layer2/embedding.py`
- **Loads once via `@lru_cache`**, runs on CPU, completely free
- **DO NOT revert to blake2b/SHA256 hashing** — that was the original critical bug

### Skill Taxonomy
- **Central registry:** `PlacedOn/skill_taxonomy.py`
- 7 behavioral HCV blocks: `block_4_grit`, `block_5_resilience`, `block_6_social`, `block_6_leadership`, `block_8_ownership`, `block_8_curiosity`, `block_10_calibration`
- 7 technical skills: `caching`, `system_design`, `db_design`, `backend`, `frontend`, `ui`, `performance`
- `JD_SKILL_MAP` normalizes JD keywords → canonical skill IDs

### API Endpoints
- `POST /ingest/csv` — LinkedIn CSV work history upload
- `POST /rating` — 90-day employer rating (green/yellow/red)
- `POST /export/jsonl` — Training data pipeline
- `GET /health` — Health check
- `WS /ws/{interview_id}` — Interview WebSocket
- `WS /interaction/ws/{session_id}` — Voice pipeline WebSocket

### Zero-Cost Stack
- **Database:** Supabase (Postgres + pgvector, 500MB free)
- **Hosting:** Vercel or Render (free tier)
- **Embeddings:** sentence-transformers (local CPU, free)
- **Redis:** Upstash (256MB free)

## Testing

All test directories have `__init__.py` files to prevent pytest module conflicts.
Current status: **54 tests passing** across all layers.

## Important Notes

1. **PYTHONPATH must include both `PlacedOn` and `PlacedOn/backend`** for all imports to resolve
2. The `skill_taxonomy.py` is imported as a top-level module from the `PlacedOn/` directory
3. Supabase integration is stubbed with `# TODO` comments — wire when credentials are configured
4. The trust trigger fires once per interview at the 5-minute mark via WebSocket
