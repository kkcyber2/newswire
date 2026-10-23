"""Source adapters.

`fetch_*` functions return `Item` objects. The demo source is deterministic so the
test suite and the CLI produce the same feed every time.
"""
from __future__ import annotations

import json
from typing import Any, Callable

from .models import Item

# A fetcher takes no arguments and returns a list of Items.
Fetcher = Callable[[], list[Item]]


def items_from_json(payload: str, *, source: str) -> list[Item]:
    """Parse a JSON array of {title, url, published, summary} into Items."""
    try:
        rows = json.loads(payload)
    except ValueError as exc:
        raise ValueError(f"source payload is not valid JSON: {exc}") from exc
    if not isinstance(rows, list):
        raise ValueError("source payload must be a JSON array")
    items: list[Item] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or "title" not in row:
            raise ValueError(f"row {index} has no title")
        items.append(
            Item(
                id=str(row.get("id") or f"{source}-{index}"),
                title=str(row["title"]),
                url=str(row.get("url", "")),
                source=str(row.get("source", source)),
                published=float(row.get("published", 0.0)),
                summary=str(row.get("summary", "")),
            )
        )
    return items


# A fixed "now" keeps the demo feed reproducible.
DEMO_NOW = 1_800_000_000.0

_DEMO_ROWS: list[dict[str, Any]] = [
    {"id": "a1", "title": "Federal Reserve holds interest rates steady", "source": "reuters",
     "url": "https://example.com/a1", "published": DEMO_NOW - 600,
     "summary": "The central bank left its benchmark rate unchanged, citing cooling inflation."},
    {"id": "a2", "title": "Federal Reserve leaves interest rates unchanged at latest meeting", "source": "ap",
     "url": "https://example.com/a2", "published": DEMO_NOW - 900,
     "summary": "Policymakers voted to keep the target range where it is."},
    {"id": "a3", "title": "Federal Reserve keeps rates steady, signals patience", "source": "bbc",
     "url": "https://example.com/a3", "published": DEMO_NOW - 1200, "summary": ""},
    {"id": "b1", "title": "New WebGL standard ships in browsers", "source": "arstechnica",
     "url": "https://example.com/b1", "published": DEMO_NOW - 1800,
     "summary": "The updated specification adds compute shader support."},
    {"id": "b2", "title": "Browsers roll out the updated WebGL standard", "source": "theverge",
     "url": "https://example.com/b2", "published": DEMO_NOW - 2400, "summary": ""},
    {"id": "c1", "title": "Startup raises Series B for developer tooling", "source": "techcrunch",
     "url": "https://example.com/c1", "published": DEMO_NOW - 3600,
     "summary": "The round was led by an existing investor."},
    {"id": "d1", "title": "Open source maintainers report burnout at record levels", "source": "hn",
     "url": "https://example.com/d1", "published": DEMO_NOW - 7200,
     "summary": "A survey of 4,000 maintainers found rising workload."},
    {"id": "d2", "title": "Open source maintainers report burnout at record levels, survey finds", "source": "blog",
     "url": "https://example.com/d2", "published": DEMO_NOW - 8000, "summary": ""},
    {"id": "e1", "title": "Quantum error correction milestone reported", "source": "guardian",
     "url": "https://example.com/e1", "published": DEMO_NOW - 10_000,
     "summary": "Researchers demonstrated a logical qubit below threshold."},
    {"id": "f1", "title": "City council approves new transit line", "source": "bbc",
     "url": "https://example.com/f1", "published": DEMO_NOW - 20_000, "summary": ""},
]


def demo_items() -> list[Item]:
    """A deterministic multi-source feed, including deliberate duplicates."""
    return items_from_json(json.dumps(_DEMO_ROWS), source="demo")
