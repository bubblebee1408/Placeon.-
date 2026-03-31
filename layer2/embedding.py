import hashlib
import math
import re


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


async def embed_text(text: str) -> list[float]:
    tokens = _tokens(text)
    token_count = max(len(tokens), 1)
    unique_count = max(len(set(tokens)), 1)

    dimension = max(8, min(unique_count * 2 + (token_count % 5), 48))

    values: list[float] = []
    for idx in range(dimension):
        digest = hashlib.sha256(f"{text}|{idx}".encode("utf-8")).hexdigest()
        value = int(digest[:8], 16) / 0xFFFFFFFF
        values.append((value * 2.0) - 1.0)

    return _l2_normalize(values)


def cosine_similarity(left: list[float], right: list[float]) -> float:
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
    return 1.0 - ((cosine_similarity(left, right) + 1.0) / 2.0)


def _l2_normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm <= 0:
        return vector
    return [value / norm for value in vector]
