from newswire.text import (
    jaccard,
    shingle_similarity,
    shingles,
    title_similarity,
    token_set,
    tokenize,
)


def test_tokenize_drops_stopwords():
    assert "the" not in tokenize("the fed holds rates")


def test_token_set_is_a_set():
    # 'fed' expands to 'federal reserve' before tokenising.
    assert token_set("fed fed rates") == {"federal", "reserve", "rates"}


def test_jaccard_identical_sets():
    assert jaccard({"a", "b"}, {"a", "b"}) == 1.0


def test_jaccard_disjoint_sets():
    assert jaccard({"a"}, {"b"}) == 0.0


def test_jaccard_both_empty_is_one():
    assert jaccard(set(), set()) == 1.0


def test_shingles_are_word_trigrams():
    assert shingles("one two three four", 3) == {"one two three", "two three four"}


def test_shingles_of_a_short_string():
    assert shingles("one two", 3) == {"one two"}


def test_shingles_of_empty_string():
    assert shingles("", 3) == set()


def test_shingle_similarity_catches_reordering():
    a = "fed holds rates steady"
    b = "rates steady fed holds"
    assert shingle_similarity(a, b) < 1.0
    assert shingle_similarity(a, a) == 1.0


def test_title_similarity_matches_paraphrase():
    assert title_similarity(
        "Federal Reserve holds interest rates steady",
        "Fed leaves rates unchanged at latest meeting",
    ) > 0.2


def test_title_similarity_of_unrelated_titles_is_low():
    assert title_similarity(
        "Federal Reserve holds interest rates steady",
        "City council approves new transit line",
    ) < 0.1
