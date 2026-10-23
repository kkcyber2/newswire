from newswire.models import Item
from newswire.rank import (
    corroboration_factor,
    rank,
    recency_factor,
    score_item,
    source_weight,
)

NOW = 1_800_000_000.0


def item(id_, source="reuters", published=None, sources=None):
    return Item(
        id=id_,
        title=f"title {id_}",
        url="",
        source=source,
        published=NOW - 600 if published is None else published,
        sources=sources or [source],
    )


def test_recency_is_one_for_now():
    assert recency_factor(NOW, now=NOW) == 1.0


def test_recency_halves_after_one_half_life():
    assert abs(recency_factor(NOW - 18 * 3600, now=NOW) - 0.5) < 1e-9


def test_recency_never_goes_negative_for_future_items():
    assert recency_factor(NOW + 10_000, now=NOW) == 1.0


def test_known_source_weights():
    assert source_weight("reuters") == 1.0
    assert source_weight("reddit") == 0.4


def test_unknown_source_gets_the_default():
    assert source_weight("some-blog") == 0.5


def test_source_weight_is_case_insensitive():
    assert source_weight("Reuters") == 1.0


def test_corroboration_grows_with_sources():
    assert corroboration_factor(["a"]) == 1.0
    assert corroboration_factor(["a", "b"]) == 2.0
    assert corroboration_factor(["a", "b", "c", "d"]) == 3.0


def test_corroboration_is_logarithmic():
    two = corroboration_factor(["a", "b"])
    ten = corroboration_factor([str(i) for i in range(10)])
    assert ten < two * 4


def test_score_item_records_its_components():
    scored = score_item(item("a"), now=NOW)
    assert set(scored.score_parts) == {"source", "recency", "corroboration"}
    assert scored.score > 0


def test_rank_orders_by_score_descending():
    items = [
        item("old", "reuters", published=NOW - 100_000),
        item("fresh", "reuters", published=NOW - 60),
    ]
    ranked = rank(items, now=NOW)
    assert ranked[0].id == "fresh"


def test_corroboration_can_outweigh_recency():
    items = [
        item("solo", "reuters", published=NOW - 60, sources=["reuters"]),
        item("shared", "bbc", published=NOW - 3600, sources=["bbc", "ap", "reuters", "guardian"]),
    ]
    ranked = rank(items, now=NOW)
    assert ranked[0].id == "shared"


def test_rank_is_stable_for_equal_scores():
    items = [item("b"), item("a")]
    assert [i.id for i in rank(items, now=NOW)] == ["a", "b"]
