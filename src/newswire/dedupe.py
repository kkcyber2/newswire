"""Collapse the same story reported by several outlets."""
from __future__ import annotations

from .models import Item
from .text import title_similarity

DEFAULT_THRESHOLD = 0.38


def dedupe(items: list[Item], *, threshold: float = DEFAULT_THRESHOLD) -> tuple[list[Item], int]:
    """Merge near-identical items, keeping the earliest as the canonical one.

    Returns (kept_items, number_removed). The canonical item accumulates the other
    outlets in `sources` and their ids in `duplicates`, so nothing is lost.

    This is single-linkage clustering, so it is computed with union-find over every
    pair rather than a greedy first-match scan. A greedy scan is order-dependent and
    breaks on chaining: if A is similar to B and B is similar to C, but A is not
    similar to C, then whichever of A or C is visited first claims B and the story
    splits in two. Union-find merges the whole connected component regardless of
    order.
    """
    ordered = sorted(items, key=lambda i: (i.published, i.id))
    count = len(ordered)
    parent = list(range(count))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[max(left_root, right_root)] = min(left_root, right_root)

    for i in range(count):
        for j in range(i + 1, count):
            if title_similarity(ordered[i].title, ordered[j].title) >= threshold:
                union(i, j)

    groups: dict[int, list[int]] = {}
    for index in range(count):
        groups.setdefault(find(index), []).append(index)

    kept: list[Item] = []
    removed = 0
    # Iterate groups in the order of their earliest member, so the output stays
    # ordered by publication time.
    for root in sorted(groups, key=lambda r: min(groups[r])):
        members = groups[root]
        canonical = ordered[members[0]]
        canonical.sources = [canonical.source]
        canonical.duplicates = []
        for index in members[1:]:
            other = ordered[index]
            removed += 1
            if other.source not in canonical.sources:
                canonical.sources.append(other.source)
            canonical.duplicates.append(other.id)
            # Keep the longer summary; it usually carries more of the story.
            if len(other.summary) > len(canonical.summary):
                canonical.summary = other.summary
        kept.append(canonical)
    return kept, removed
