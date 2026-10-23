"""Group deduped items into topics by shared vocabulary."""
from __future__ import annotations

from .models import Item, Topic
from .text import jaccard, token_set

DEFAULT_THRESHOLD = 0.18


def _label(items: list[Item], *, words: int = 3) -> str:
    """Name a topic after its most distinctive shared terms."""
    counts: dict[str, int] = {}
    for item in items:
        for token in token_set(item.title):
            counts[token] = counts.get(token, 0) + 1
    # Prefer terms that appear in more than one item, then by frequency.
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    shared = [term for term, count in ranked if count > 1][:words]
    if not shared:
        shared = [term for term, _ in ranked[:words]]
    return " · ".join(shared) if shared else "misc"


def cluster(items: list[Item], *, threshold: float = DEFAULT_THRESHOLD) -> list[Topic]:
    """Agglomerative clustering: merge the closest pair until nothing is close enough.

    The number of topics is discovered rather than fixed, because a feed's topic count
    is not known in advance.
    """
    groups: list[list[Item]] = [[item] for item in items]
    while True:
        best: tuple[float, int, int] | None = None
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                similarity = _group_similarity(groups[i], groups[j])
                if similarity >= threshold and (best is None or similarity > best[0]):
                    best = (similarity, i, j)
        if best is None:
            break
        _, i, j = best
        groups[i] = groups[i] + groups[j]
        del groups[j]

    topics: list[Topic] = []
    for index, group in enumerate(groups):
        group.sort(key=lambda item: -item.score)
        topics.append(Topic(id=f"t{index + 1:02d}", label=_label(group), items=group))
    topics.sort(key=lambda topic: (-topic.weight, topic.id))
    return topics


def _group_similarity(a: list[Item], b: list[Item]) -> float:
    """Average pairwise title similarity between two groups."""
    total = 0.0
    pairs = 0
    for left in a:
        left_tokens = token_set(left.title)
        for right in b:
            total += jaccard(left_tokens, token_set(right.title))
            pairs += 1
    return total / pairs if pairs else 0.0
