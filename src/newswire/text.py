"""Tokenisation, shingling and similarity for the dedupe and cluster steps."""
from __future__ import annotations

import re

_WORD = re.compile(r"[a-z0-9]+")

STOPWORDS = frozenset(
    """a an and are as at be been by for from had has have in into is it its of on or
    that the their there these this to was were will with says say said after before
    over under about more than new""".split()
)


# News copy abbreviates relentlessly: "Fed" and "Federal Reserve" are the same actor,
# and a bag-of-words comparison sees them as unrelated. Expanding the common ones
# before tokenising is what lets paraphrase dedupe actually work.
SYNONYMS: dict[str, str] = {
    "fed": "federal reserve",
    "feds": "federal reserve",
    "boe": "bank of england",
    "ecb": "european central bank",
    "gop": "republican",
    "dems": "democrat",
    "uk": "united kingdom",
    "us": "united states",
    "ai": "artificial intelligence",
    "ml": "machine learning",
    "ceo": "chief executive",
    "cfo": "chief financial",
    "ipo": "initial public offering",
    "gdp": "gross domestic product",
    "cpi": "consumer price index",
}


def expand_synonyms(text: str) -> str:
    """Replace known abbreviations with their full form, word by word."""
    words = _WORD.findall(text.lower())
    return " ".join(SYNONYMS.get(word, word) for word in words)


def tokenize(text: str) -> list[str]:
    expanded = expand_synonyms(text)
    return [w for w in _WORD.findall(expanded) if w not in STOPWORDS and len(w) > 1]


def token_set(text: str) -> set[str]:
    return set(tokenize(text))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def shingles(text: str, size: int = 3) -> set[str]:
    """Word n-grams, which catch reordered headlines that bag-of-words misses."""
    words = tokenize(text)
    if len(words) < size:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i : i + size]) for i in range(len(words) - size + 1)}


def shingle_similarity(a: str, b: str, size: int = 3) -> float:
    return jaccard(shingles(a, size), shingles(b, size))


def title_similarity(a: str, b: str) -> float:
    """Blend of bag-of-words and shingle overlap.

    Bag-of-words catches paraphrase; shingles catch word order. Taking the max means
    either signal alone is enough to call two headlines the same story.
    """
    return max(jaccard(token_set(a), token_set(b)), shingle_similarity(a, b))
