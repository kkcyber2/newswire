import json

from newswire.pipeline import run_pipeline
from newswire.sources import DEMO_NOW, demo_items, items_from_json


def test_demo_feed_is_deterministic():
    first = run_pipeline(demo_items())
    second = run_pipeline(demo_items())
    assert [i.id for i in first.items] == [i.id for i in second.items]


def test_pipeline_removes_the_planted_duplicates():
    feed = run_pipeline(demo_items())
    assert feed.fetched == 10
    assert feed.duplicates_removed >= 3
    assert len(feed.items) < feed.fetched


def test_pipeline_produces_topics():
    feed = run_pipeline(demo_items())
    assert feed.topics
    assert sum(t.size for t in feed.topics) == len(feed.items)


def test_every_item_has_a_score_and_sources():
    feed = run_pipeline(demo_items())
    for item in feed.items:
        assert item.score > 0
        assert item.sources
        assert item.score_parts


def test_the_fed_story_is_corroborated_by_three_outlets():
    feed = run_pipeline(demo_items())
    fed = next(i for i in feed.items if "reserve" in i.title.lower() or "fed " in i.title.lower())
    assert len(fed.sources) >= 3


def test_items_are_ranked_descending():
    feed = run_pipeline(demo_items())
    scores = [i.score for i in feed.items]
    assert scores == sorted(scores, reverse=True)


def test_items_from_json_parses_a_payload():
    payload = json.dumps([{"title": "Hello", "url": "https://x", "published": 1.0}])
    items = items_from_json(payload, source="test")
    assert items[0].title == "Hello"
    assert items[0].source == "test"


def test_items_from_json_rejects_bad_json():
    import pytest

    with pytest.raises(ValueError, match="valid JSON"):
        items_from_json("{nope", source="test")


def test_items_from_json_rejects_a_non_array():
    import pytest

    with pytest.raises(ValueError, match="array"):
        items_from_json('{"a":1}', source="test")


def test_items_from_json_rejects_a_row_without_a_title():
    import pytest

    with pytest.raises(ValueError, match="no title"):
        items_from_json('[{"url":"x"}]', source="test")


def test_public_feed_is_serialisable():
    json.dumps(run_pipeline(demo_items()).public())


def test_pipeline_accepts_an_explicit_now():
    feed = run_pipeline(demo_items(), now=DEMO_NOW + 100_000)
    assert feed.items
