from __future__ import annotations

from datetime import datetime, timezone
from math import exp, sqrt

from .config import DECAY_RATE, W_FREQ, W_REC, W_SIM, SIMILARITY_FLOOR


def composite_score(
    similarity: float,
    last_accessed_at: str,
    access_count: int,
    max_access_count: int,
    importance: float = 0.5,
) -> float:
    """Compute a weighted composite score for memory ranking.

    Formula:
        recency  = exp(-DECAY_RATE * hours_since_access)
        frequency = min(access_count / max(max_access_count, 1), 1.0)
        raw = similarity * W_SIM + recency * W_REC + frequency * W_FREQ
        if similarity >= SIMILARITY_FLOOR: raw = max(raw, similarity * 0.6)
        score = raw * sqrt(importance)
    """
    hours = _hours_since(last_accessed_at)
    recency = exp(-DECAY_RATE * hours)
    frequency = min(access_count / max(max_access_count, 1), 1.0)
    raw = similarity * W_SIM + recency * W_REC + frequency * W_FREQ
    if similarity >= SIMILARITY_FLOOR:
        raw = max(raw, similarity * 0.6)
    return raw * sqrt(importance)


def _hours_since(iso_timestamp: str) -> float:
    """Return hours elapsed since *iso_timestamp* (ISO-8601)."""
    dt = datetime.fromisoformat(iso_timestamp)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - dt
    return max(delta.total_seconds() / 3600, 0.0)
