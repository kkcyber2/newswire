"""Transparent ranking: source weight, recency decay and corroboration."""
from __future__ import annotations

import math

from .models import Item

# How much each outlet is trusted. A real deployment would learn these.
SOURCE_WEIGHTS: dict[str, float] = {
    "reuters": 1.0,
    "ap": 1.0,
    "bbc": 0.95,
    "guardian": 0.9,
    "arstechnica": 0.9,
    "theverge": 0.85,
    "techcrunch": 0.8,
    "hn": 0.6,
    "reddit": 0.4,
    "blog": 0.35,
}
DEFAULT_SOURCE_WEIGHT = 0.5

# Score halves roughly every this many hours.
HALF_LIFE_HOURS = 18.0


def recency_factor(published: float, *, now: float) -> float:
    """Exponential decay in [0, 1], 1.0 for something published right now."""
    age_hours = max(0.0, (now - published) / 3600.0)
    return math.pow(0.5, age_hours / HALF_LIFE_HOURS)


def source_weight(source: str) -> float:
    return SOURCE_WEIGHTS.get(source.lower(), DEFAULT_SOURCE_WEIGHT)


def corroboration_factor(sources: list[str]) -> float:
    """More independent outlets carrying a story means it matters more.

    Logarithmic, so the tenth outlet adds far less than the second.
    """
    return 1.0 + math.log2(max(1, len(sources)))


def score_item(item: Item, *, now: float) -> Item:
    """Compute and attach the score, keeping every component for inspection."""
    parts = {
        "source": source_weight(item.source),
        "recency": recency_factor(item.published, now=now),
        "corroboration": corroboration_factor(item.sources or [item.source]),
    }
    item.score_parts = parts
    item.score = parts["source"] * parts["recency"] * parts["corroboration"]
    return item


def rank(items: list[Item], *, now: float) -> list[Item]:
    for item in items:
        score_item(item, now=now)
    return sorted(items, key=lambda i: (-i.score, i.id))
