"""Feed item and topic models."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Item:
    id: str
    title: str
    url: str
    source: str
    published: float
    summary: str = ""
    score: float = 0.0
    score_parts: dict[str, float] = field(default_factory=dict)
    sources: list[str] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)

    def public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "published": self.published,
            "summary": self.summary,
            "score": round(self.score, 4),
            "score_parts": {k: round(v, 4) for k, v in self.score_parts.items()},
            "sources": self.sources,
            "duplicates": self.duplicates,
        }


@dataclass
class Topic:
    id: str
    label: str
    items: list[Item] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.items)

    @property
    def weight(self) -> float:
        return sum(item.score for item in self.items)

    def public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "size": self.size,
            "weight": round(self.weight, 4),
            "items": [item.public() for item in self.items],
        }


@dataclass
class Feed:
    items: list[Item] = field(default_factory=list)
    topics: list[Topic] = field(default_factory=list)
    fetched: int = 0
    duplicates_removed: int = 0

    def public(self) -> dict[str, Any]:
        return {
            "fetched": self.fetched,
            "duplicates_removed": self.duplicates_removed,
            "items": [i.public() for i in self.items],
            "topics": [t.public() for t in self.topics],
        }
