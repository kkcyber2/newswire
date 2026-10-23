from newswire.dedupe import dedupe
from newswire.models import Item


def item(id_, title, source="reuters", published=1000.0, summary=""):
    return Item(id=id_, title=title, url=f"https://example.com/{id_}", source=source,
                published=published, summary=summary)


def test_identical_titles_collapse():
    items = [
        item("a", "Fed holds rates steady", "reuters", 1000),
        item("b", "Fed holds rates steady", "ap", 1100),
    ]
    kept, removed = dedupe(items)
    assert len(kept) == 1
    assert removed == 1


def test_paraphrased_titles_collapse():
    items = [
        item("a", "Federal Reserve holds interest rates steady", "reuters", 1000),
        item("b", "Fed leaves rates unchanged at latest meeting", "ap", 1100),
    ]
    kept, removed = dedupe(items, threshold=0.3)
    assert len(kept) == 1
    assert removed == 1


def test_unrelated_titles_are_kept():
    items = [
        item("a", "Fed holds rates steady", "reuters", 1000),
        item("b", "City council approves transit line", "bbc", 1100),
    ]
    kept, removed = dedupe(items)
    assert len(kept) == 2
    assert removed == 0


def test_the_earliest_item_is_canonical():
    items = [
        item("late", "Fed holds rates steady", "ap", 2000),
        item("early", "Fed holds rates steady", "reuters", 1000),
    ]
    kept, _ = dedupe(items)
    assert kept[0].id == "early"


def test_sources_accumulate_on_the_canonical_item():
    items = [
        item("a", "Fed holds rates steady", "reuters", 1000),
        item("b", "Fed holds rates steady", "ap", 1100),
        item("c", "Fed holds rates steady", "bbc", 1200),
    ]
    kept, _ = dedupe(items)
    assert sorted(kept[0].sources) == ["ap", "bbc", "reuters"]
    assert sorted(kept[0].duplicates) == ["b", "c"]


def test_a_source_is_not_listed_twice():
    items = [
        item("a", "Fed holds rates steady", "reuters", 1000),
        item("b", "Fed holds rates steady", "reuters", 1100),
    ]
    kept, _ = dedupe(items)
    assert kept[0].sources == ["reuters"]


def test_the_longer_summary_wins():
    items = [
        item("a", "Fed holds rates steady", "reuters", 1000, summary="short"),
        item("b", "Fed holds rates steady", "ap", 1100, summary="a much longer summary of the story"),
    ]
    kept, _ = dedupe(items)
    assert kept[0].summary == "a much longer summary of the story"


def test_chained_similarity_merges_the_whole_cluster():
    # A~B and B~C but A!~C. Comparing only against the canonical title would split
    # this into two clusters; comparing against every member keeps it as one.
    items = [
        item("a", "Federal Reserve holds interest rates steady", "reuters", 1000),
        item("b", "Federal Reserve leaves interest rates unchanged at latest meeting", "ap", 1100),
        item("c", "Federal Reserve keeps rates steady, signals patience", "bbc", 1200),
    ]
    kept, removed = dedupe(items)
    assert len(kept) == 1
    assert removed == 2
    assert sorted(kept[0].sources) == ["ap", "bbc", "reuters"]


def test_heavy_paraphrase_is_not_merged():
    # An honest limitation: a purely lexical deduper cannot see that "holds rates
    # steady" and "leaves rates unchanged" are the same story unless the wording
    # overlaps. Real wire copy is near-verbatim, which is why this works in practice.
    items = [
        item("a", "Central bank holds borrowing costs steady", "reuters", 1000),
        item("b", "Monetary authority leaves its benchmark unchanged", "ap", 1100),
    ]
    kept, removed = dedupe(items)
    assert len(kept) == 2
    assert removed == 0


def test_empty_input():
    assert dedupe([]) == ([], 0)
