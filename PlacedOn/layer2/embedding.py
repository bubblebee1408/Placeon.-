"""
PlacedOn Layer 2 - Semantic Embedding Engine

Primary path: sentence-transformers SBERT (all-MiniLM-L6-v2) when it is
already available locally.

Fallback path: deterministic lightweight lexical embeddings so tests,
simulation, and low-cost deployments still work without network downloads.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import math
import re
from collections import Counter
from functools import lru_cache
from typing import Protocol

from skill_taxonomy import SKILL_KEYWORDS, SKILL_PROMPTS, signal_terms

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # noqa: BLE001
    SentenceTransformer = None

_LOGGER = logging.getLogger(__name__)

_MODEL_NAME = "all-MiniLM-L6-v2"
_DIMENSION = 384
_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")
_FALLBACK_ANCHOR_DIM = 160
_ANCHOR_ALIASES = {
    "aligned": "align",
    "aligning": "align",
    "alignment": "align",
    "stakeholders": "stakeholder",
    "listening": "listen",
    "listened": "listen",
    "ownership": "own",
    "owned": "own",
    "owner": "own",
    "responsibility": "responsible",
    "responsibilities": "responsible",
    "recovery": "recover",
    "recovered": "recover",
    "recovering": "recover",
    "followed": "follow",
    "follows": "follow",
    "following": "follow",
    "learned": "learn",
    "learning": "learn",
    "validated": "validate",
    "validating": "validate",
    "checked": "check",
    "checking": "check",
    "questions": "question",
    "tradeoffs": "tradeoff",
}


class _EmbeddingBackend(Protocol):
    def encode(self, sentences: str | list[str]) -> list[float] | list[list[float]]:
        ...


def _normalize_token(token: str) -> str:
    token = token.lower()
    token = re.sub(r"[^a-z0-9]+", "", token)
    if not token:
        return ""
    token = _ANCHOR_ALIASES.get(token, token)

    for suffix in ("ingly", "edly", "ing", "ed", "ly", "ies", "es", "s"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            if suffix == "ies":
                token = token[:-3] + "y"
            else:
                token = token[: -len(suffix)]
            break

    return _ANCHOR_ALIASES.get(token, token)


def _tokenize(text: str) -> list[str]:
    tokens = [_normalize_token(match.group(0)) for match in _TOKEN_RE.finditer(text.lower())]
    return [token for token in tokens if token]


@lru_cache(maxsize=1)
def _fallback_anchor_terms() -> tuple[str, ...]:
    terms: set[str] = set()

    for prompt in SKILL_PROMPTS.values():
        terms.update(_tokenize(prompt))

    for keywords in SKILL_KEYWORDS.values():
        for keyword in keywords:
            terms.update(_tokenize(keyword))

    terms.update(_tokenize(" ".join(sorted(signal_terms()))))
    terms.update(
        {
            _normalize_token(term)
            for term in {
                "team",
                "deadline",
                "risk",
                "recover",
                "stakeholder",
                "align",
                "follow",
                "through",
                "pressure",
                "feedback",
                "tradeoff",
                "example",
                "clarify",
                "communicate",
                "reliability",
                "ownership",
            }
        }
    )

    ordered = tuple(sorted(term for term in terms if len(term) >= 3))
    return ordered[:_FALLBACK_ANCHOR_DIM]


def _hash_bucket(feature: str) -> tuple[int, float]:
    digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
    bucket = _FALLBACK_ANCHOR_DIM + (int.from_bytes(digest[:4], "big") % (_DIMENSION - _FALLBACK_ANCHOR_DIM))
    sign = 1.0 if digest[4] % 2 == 0 else -1.0
    return bucket, sign


def _normalized_vector(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        return vector
    return [value / norm for value in vector]


def _encode_with_fallback(text: str) -> list[float]:
    text = (text or "").strip()
    if not text:
        return [0.0] * _DIMENSION

    tokens = _tokenize(text)
    if not tokens:
        return [0.0] * _DIMENSION

    counts = Counter(tokens)
    total = float(sum(counts.values()) or 1.0)
    vector = [0.0] * _DIMENSION
    anchor_terms = _fallback_anchor_terms()

    for idx, term in enumerate(anchor_terms):
        count = counts.get(term)
        if count:
            vector[idx] = count / total

    for token, count in counts.items():
        bucket, sign = _hash_bucket(f"uni:{token}")
        vector[bucket] += sign * (count / total)

    for idx in range(len(tokens) - 1):
        bucket, sign = _hash_bucket(f"bi:{tokens[idx]}::{tokens[idx + 1]}")
        vector[bucket] += sign * 0.6

    for idx in range(len(tokens) - 2):
        bucket, sign = _hash_bucket(f"tri:{tokens[idx]}::{tokens[idx + 1]}::{tokens[idx + 2]}")
        vector[bucket] += sign * 0.3

    if any(token in {"because", "therefore", "however", "tradeoff"} for token in tokens):
        vector[-4] = 0.8
    if any(token in {"align", "stakeholder", "team", "listen"} for token in tokens):
        vector[-3] = 0.8
    vector[-2] = min(len(tokens) / 40.0, 1.0)
    vector[-1] = 1.0 if text.endswith((".", "!", "?")) else 0.5

    return _normalized_vector(vector)


class _FallbackSentenceTransformer:
    def encode(self, sentences: str | list[str]) -> list[float] | list[list[float]]:
        if isinstance(sentences, str):
            return _encode_with_fallback(sentences)
        return [_encode_with_fallback(sentence) for sentence in sentences]


@lru_cache(maxsize=1)
def _load_model() -> _EmbeddingBackend:
    """Load a local SBERT model when available, otherwise use the offline fallback."""
    if SentenceTransformer is not None:
        try:
            return SentenceTransformer(_MODEL_NAME, local_files_only=True)
        except Exception as exc:  # noqa: BLE001
            _LOGGER.warning(
                "Layer2 embedding fallback activated because '%s' was unavailable locally: %s",
                _MODEL_NAME,
                exc,
            )
    else:
        _LOGGER.warning("sentence-transformers import failed; using deterministic fallback embeddings")

    return _FallbackSentenceTransformer()


async def embed_text(text: str) -> list[float]:
    """Generate a 384-dim semantic embedding for the given text."""
    text = (text or "").strip()
    if not text:
        return [0.0] * _DIMENSION

    model = _load_model()
    vector = await asyncio.to_thread(model.encode, text)
    if hasattr(vector, "tolist"):
        return vector.tolist()
    return list(vector)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not left or not right:
        return 0.0

    max_len = max(len(left), len(right))
    l = left + [0.0] * (max_len - len(left))
    r = right + [0.0] * (max_len - len(right))

    dot = sum(a * b for a, b in zip(l, r))
    norm_l = math.sqrt(sum(a * a for a in l))
    norm_r = math.sqrt(sum(b * b for b in r))

    if norm_l == 0.0 or norm_r == 0.0:
        return 0.0

    score = dot / (norm_l * norm_r)
    return max(-1.0, min(score, 1.0))


def cosine_distance(left: list[float], right: list[float]) -> float:
    """Cosine distance normalized to [0, 1]."""
    return 1.0 - ((cosine_similarity(left, right) + 1.0) / 2.0)
