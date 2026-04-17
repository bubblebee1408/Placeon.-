# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

**PlacedOn** is an AI-powered hiring platform. The repo contains both product/business documentation AND active implementation code.

**Active implementation lives in:**
- `PlacedOn/backend/` — FastAPI server (Python), the core interview engine
- `PlacedOn/interaction_layer/` — Real-time voice/session/turn orchestration layer
- `PlacedOn/pre-interview/` — React + Vite + Tailwind frontend (pre-interview screen, Gemini API)

Documentation (strategy, specs, research) lives in `PlacedOn-Research/product/`, `PlacedOn-Research/business/`, `PlacedOn-Research/research/`, `PlacedOn-Research/Markovian-Reasoning/`.

## Development Commands

### Backend (FastAPI)

```bash
cd PlacedOn/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start Redis (required)
redis-server
# or: docker run --rm -p 6379:6379 redis:7

# Run server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run all tests
python3 -m pytest -q

# Run a single test file
python3 -m pytest tests/test_websocket.py -q

# Manual WebSocket test client
python3 manual_ws_client.py --url http://127.0.0.1:8000 --interview-id demo-1
```

Environment variables (all optional, have defaults):
```
REDIS_URL=redis://localhost:6379/0
SESSION_TTL_SECONDS=1800
STREAM_DELAY_SECONDS=0.05
INITIAL_QUESTION="Tell me about a backend system you designed recently."
```

### Frontend (pre-interview screen)

```bash
cd PlacedOn/pre-interview
npm install
# Set GEMINI_API_KEY in .env.local
npm run dev        # runs on port 3000
npm run build
npm run lint       # tsc --noEmit
```

## Code Architecture

### Backend Layer (`PlacedOn/backend/`)

**Entry point:** `app/main.py` — FastAPI app with lifespan setup (Redis session manager, LiveInterviewRuntime).

**Two WebSocket endpoints** in `app/websocket_router.py` and `app/interaction_router.py`:
- `/ws/{interview_id}` — Simple stateful text interview. Handles reconnection, idempotency via `message_id`, token streaming.
- `/interaction/ws/{session_id}` — Full voice pipeline: receives audio chunks → STT → turn completion detection → backend processing → persona streaming + TTS audio frames.

**HTTP endpoints** in `app/interaction_router.py`:
- `POST /generate-question` — Stateful question generation (intro phase → technical phase). Uses in-memory dict `_interview_pipeline_state` keyed by `session_id`.
- `POST /evaluate-answer` — Scores answer, updates state with evaluation.
- `POST /process-turn` — Used internally by interaction layer to advance interview state.
- `GET/POST /tts/voices`, `/tts/speak` — Mac system TTS.

**Pipeline** (`pipeline/`):
- `conversation_orchestrator.py` — Generates intro question via Ollama (`llama3`).
- `planner.py` — Decides next interview action (deepen/broaden/pivot/close).
- `context_builder.py` — Builds structured context from candidate + job profiles.
- `question_strategy.py` — Strategy selection logic.

**LLM layer** (`llm/`):
- `ollama_client.py` — Calls local Ollama instance (default model: `llama3`).
- `generator.py` — Generates interview questions given a plan and context.
- `judge.py` — Evaluates candidate answers; returns score + missing concepts.

**Session management** (`app/session_manager.py`) — Redis-backed, async, TTL-based. Key format: `interview:{interview_id}`.

**State compression** (`app/state_compressor.py`) — Compresses state to ≤400 chars to keep LLM context bounded (O(1) complexity property of the Markov engine).

**Schemas** (`schemas/`): `generator_schema.py` (CandidateProfile, JobProfile, question output), `judge_schema.py` (answer evaluation output).

### Interaction Layer (`PlacedOn/interaction_layer/`)

Sits above the backend. Handles real-time voice I/O, does NOT do reasoning. Components:
- `voice/stt.py`, `voice/tts.py` — Currently mock implementations.
- `communication/websocket_manager.py` — Connection lifecycle.
- `session/session_manager.py` — Session timeout, silence detection, turn counting.
- `turn/turn_manager.py` — Collects transcript, detects completion (final event / explicit stop / silence), submits to backend via `POST /process-turn`.
- `persona/persona_engine.py` — Streams backend response tokens (no generation).
- `monitoring/presence.py` — Camera/tab/latency presence snapshots.
- `error_handling/recovery.py` — Silence and low-confidence recovery actions.

### Frontend (`PlacedOn/pre-interview/src/`)

React + Vite + Tailwind CSS v4. Uses Gemini API (`@google/genai`) directly from client. Connects to backend at `http://localhost:8000` (CORS configured for port 3000). Uses `lucide-react` for icons and `motion` for animations.

## Important Architectural Notes

**Two parallel interview state systems exist:**
1. `InterviewState` (Pydantic model in `app/models.py`) — persisted in Redis via `SessionManager`, used by `/ws/{interview_id}` and `/interaction/ws/{session_id}`.
2. `_interview_pipeline_state` dict in `interaction_router.py` — in-memory only, used by `/generate-question` and `/evaluate-answer` endpoints. Lost on server restart.

**LLM backend is Ollama (local), not OpenAI** — The current implementation calls a local Ollama instance with `llama3`. The product spec targets OpenAI GPT-4o-mini, but the implementation uses Ollama for development.

**The interaction router imports from both `PlacedOn/backend/` and `PlacedOn/interaction_layer/`** using sys.path manipulation. The root of the repo must be in PYTHONPATH or the server must be run from the repo root.

## Product Documentation (for context)

- `PlacedOn-Research/IMPLEMENTATION-ROADMAP.md` — Phased build plan and build order
- `PlacedOn-Research/Markovian-Reasoning/AoT-for-AI-Interviewer.md` — Markov engine design (O(1) state complexity, contraction loop)
- `PlacedOn-Research/product/interviewer-model.md` — AI interviewer behavioral spec
- `PlacedOn-Research/product/bias-safety.md` — ABLEIST 8-metric bias framework (integrated at every state contraction)
- `PlacedOn-Research/product/architecture.md` — Target system design (Next.js + FastAPI + PostgreSQL + OpenAI)
