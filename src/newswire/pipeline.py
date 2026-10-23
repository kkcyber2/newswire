"""The full pipeline: fetch, dedupe, cluster, rank."""
from __future__ import annotations

from .cluster import cluster
from .dedupe import dedupe
from .models import Feed, Item
from .rank import rank
from .sources import DEMO_NOW


def run_pipeline(
    items: list[Item],
    *,
    now: float | None = None,
    dedupe_threshold: float = 0.38,
    cluster_threshold: float = 0.18,
) -> Feed:
    """Run every stage and return a ranked, clustered feed."""
    moment = now if now is not None else DEMO_NOW
    fetched = len(items)
    kept, removed = dedupe(items, threshold=dedupe_threshold)
    ranked = rank(kept, now=moment)
    topics = cluster(ranked, threshold=cluster_threshold)
    return Feed(items=ranked, topics=topics, fetched=fetched, duplicates_removed=removed)
