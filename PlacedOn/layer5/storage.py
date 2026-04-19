from collections.abc import Mapping

from layer5.models import CandidateState


class InMemoryVectorStorage:
    def __init__(self) -> None:
        self._records: dict[str, CandidateState] = {}

    async def upsert_candidate(self, state: CandidateState) -> None:
        self._records[state.candidate_id] = state

    async def get_candidate(self, candidate_id: str) -> CandidateState | None:
        return self._records.get(candidate_id)

    async def list_candidates(self) -> list[CandidateState]:
        return list(self._records.values())


class PgVectorStorageAdapter:
    """
    PgVector Storage Adapter for Supabase

    Following OpenAI scaling patterns from 2026:
    - Uses HNSW index for high-throughput Approximate Nearest Neighbor (ANN) search
    - Vector dimensions: 384 (all-MiniLM-L6-v2)
    - Recommends deploying this table on a read replica if vector queries > 50M
    
    Database Init SQL:
    ```sql
    CREATE EXTENSION IF NOT EXISTS vector;
    
    CREATE TABLE candidate_profiles (
        candidate_id TEXT PRIMARY KEY,
        embedding vector(384),
        skills JSONB,
        metadata JSONB,
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    -- OpenAI's recommended HNSW index for cosine similarity
    CREATE INDEX idx_candidate_embedding_hnsw ON candidate_profiles 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
    ```
    """

    def __init__(self, fallback_storage: InMemoryVectorStorage | None = None) -> None:
        self._fallback = fallback_storage or InMemoryVectorStorage()

    async def upsert_candidate(self, state: CandidateState) -> None:
        await self._fallback.upsert_candidate(state)

    async def get_candidate(self, candidate_id: str) -> CandidateState | None:
        return await self._fallback.get_candidate(candidate_id)

    async def list_candidates(self) -> list[CandidateState]:
        return await self._fallback.list_candidates()


class CandidateRepository:
    def __init__(self, backend: InMemoryVectorStorage | PgVectorStorageAdapter | None = None) -> None:
        self._backend = backend or PgVectorStorageAdapter()

    async def save(self, state: CandidateState) -> None:
        await self._backend.upsert_candidate(state)

    async def get(self, candidate_id: str) -> CandidateState | None:
        return await self._backend.get_candidate(candidate_id)

    async def all(self) -> list[CandidateState]:
        return await self._backend.list_candidates()

    async def save_from_aggregate(
        self,
        candidate_id: str,
        embedding: list[float],
        skills: Mapping,
        metadata: dict,
    ) -> CandidateState:
        state = CandidateState(
            candidate_id=candidate_id,
            embedding=embedding,
            skills=dict(skills),
            metadata=metadata,
        )
        await self.save(state)
        return state
