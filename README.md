# Newswire

A news aggregator that fetches from many sources, removes the duplicates, groups
related stories into topics, and ranks the result — the four steps that turn a pile of
feeds into something readable.

## The pipeline

```
fetch -> normalise -> dedupe -> cluster -> rank -> render
```

**Dedupe** is the step most aggregators get wrong. The same story arrives from six
outlets with six different headlines. Newswire compares titles by token overlap *and*
by a shingle fingerprint, so "Fed holds rates steady" and "Federal Reserve leaves rates
unchanged" collapse into one item with six sources.

**Clustering** groups the deduped items into topics by shared vocabulary, using
agglomerative merging rather than a fixed k, because the number of topics in a feed is
not known in advance.

**Ranking** is a transparent score: source weight, recency decay, and how many outlets
carried the story. Every item exposes its score components, so the ordering is
explainable rather than a black box.

## Quick start

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
newswire --demo
newswire --demo --json feed.json
newswire --demo --topics
```

## As a library

```python
from newswire.pipeline import run_pipeline
from newswire.sources import demo_items

feed = run_pipeline(demo_items())
for item in feed.items[:5]:
    print(item.score, item.title, item.sources)
```

## Tests

```bash
pytest -q
```

## License

MIT — see [LICENSE](LICENSE).

Built by **KK (Conan Sultan Khan)** · <kkdev9715@gmail.com>
[https://github.com/kkcyber2](https://github.com/kkcyber2) · LinkedIn: _add profile URL_
