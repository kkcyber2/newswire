import json

from newswire.cli import main, render
from newswire.pipeline import run_pipeline
from newswire.sources import demo_items


def test_render_lists_items():
    text = render(run_pipeline(demo_items()))
    assert "Fetched 10" in text
    assert "duplicate" in text


def test_render_topics_mode():
    text = render(run_pipeline(demo_items()), show_topics=True)
    assert "#" in text


def test_cli_demo_runs(capsys):
    assert main(["--demo"]) == 0
    assert "Fetched" in capsys.readouterr().out


def test_cli_writes_json(tmp_path, capsys):
    out = tmp_path / "feed.json"
    assert main(["--demo", "--json", str(out)]) == 0
    payload = json.loads(out.read_text())
    assert payload["fetched"] == 10
    assert payload["items"]


def test_cli_from_json(tmp_path, capsys):
    source = tmp_path / "in.json"
    source.write_text(json.dumps([{"title": "A story", "published": 1.0}]))
    assert main(["--from-json", str(source)]) == 0
    assert "A story" in capsys.readouterr().out


def test_cli_missing_file_returns_2(tmp_path):
    assert main(["--from-json", str(tmp_path / "nope.json")]) == 2
