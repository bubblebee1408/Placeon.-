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
    Simulated pgvector adapter.

    In production this can be wired to asyncpg/SQLAlchemy with a table like:
      candidate_profiles(candidate_id text primary key, embedding vector, skills jsonb, metadata jsonb)
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
