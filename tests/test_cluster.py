from newswire.cluster import cluster
from newswire.models import Item


def item(id_, title, score=1.0):
    return Item(id=id_, title=title, url="", source="reuters", published=1000.0, score=score)


def test_related_items_land_in_one_topic():
    items = [
        item("a", "Federal Reserve holds interest rates steady"),
        item("b", "Federal Reserve keeps rates steady"),
        item("c", "City council approves new transit line"),
    ]
    topics = cluster(items, threshold=0.2)
    sizes = sorted(t.size for t in topics)
    assert sizes == [1, 2]


def test_unrelated_items_each_get_their_own_topic():
    items = [
        item("a", "Quantum error correction milestone reported"),
        item("b", "City council approves new transit line"),
    ]
    assert len(cluster(items, threshold=0.2)) == 2


def test_topics_are_ordered_by_weight():
    items = [
        item("a", "Federal Reserve holds interest rates steady", score=5.0),
        item("b", "Federal Reserve keeps rates steady", score=5.0),
        item("c", "City council approves new transit line", score=0.1),
    ]
    topics = cluster(items, threshold=0.2)
    assert topics[0].weight > topics[-1].weight


def test_topic_labels_use_shared_terms():
    items = [
        item("a", "Federal Reserve holds interest rates steady"),
        item("b", "Federal Reserve keeps rates steady"),
    ]
    label = cluster(items, threshold=0.2)[0].label
    assert "reserve" in label or "rates" in label or "steady" in label


def test_items_within_a_topic_are_sorted_by_score():
    items = [
        item("a", "Federal Reserve holds interest rates steady", score=1.0),
        item("b", "Federal Reserve keeps rates steady", score=9.0),
    ]
    topic = cluster(items, threshold=0.2)[0]
    assert topic.items[0].id == "b"


def test_empty_input_gives_no_topics():
    assert cluster([]) == []


def test_a_single_item_is_its_own_topic():
    topics = cluster([item("a", "Something happened today")])
    assert len(topics) == 1
    assert topics[0].size == 1
