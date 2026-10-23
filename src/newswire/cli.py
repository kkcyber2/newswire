"""Command line entry point."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .pipeline import run_pipeline
from .sources import demo_items, items_from_json


def _stamp(value: float) -> str:
    return datetime.fromtimestamp(value, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def render(feed, *, show_topics: bool = False) -> str:
    lines = [
        f"Fetched {feed.fetched} item(s); removed {feed.duplicates_removed} duplicate(s); "
        f"{len(feed.items)} unique.",
        "",
    ]
    if show_topics:
        for topic in feed.topics:
            lines.append(f"# {topic.label}  ({topic.size} item(s), weight {topic.weight:.2f})")
            for item in topic.items:
                lines.append(f"   {item.score:5.2f}  {item.title}")
                lines.append(f"          {', '.join(item.sources)}  ·  {_stamp(item.published)}")
            lines.append("")
        return "\n".join(lines).rstrip()

    for index, item in enumerate(feed.items, start=1):
        lines.append(f"{index:2d}. [{item.score:5.2f}] {item.title}")
        lines.append(f"     {', '.join(item.sources)}  ·  {_stamp(item.published)}")
        if item.summary:
            lines.append(f"     {item.summary}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="newswire", description="Aggregate, dedupe and rank a news feed")
    parser.add_argument("--demo", action="store_true", help="use the built-in deterministic feed")
    parser.add_argument("--from-json", metavar="PATH", help="read items from a JSON file")
    parser.add_argument("--source", default="file", help="source name for --from-json")
    parser.add_argument("--topics", action="store_true", help="group the output by topic")
    parser.add_argument("--json", metavar="PATH", help="write the feed as JSON")
    args = parser.parse_args(argv)

    if args.from_json:
        try:
            items = items_from_json(Path(args.from_json).read_text(encoding="utf-8"), source=args.source)
        except (OSError, ValueError) as exc:
            print(f"could not read source: {exc}", file=sys.stderr)
            return 2
    elif args.demo:
        items = demo_items()
    else:
        parser.error("choose --demo or --from-json PATH")
        return 2

    feed = run_pipeline(items)
    print(render(feed, show_topics=args.topics))

    if args.json:
        Path(args.json).write_text(json.dumps(feed.public(), indent=2), encoding="utf-8")
        print(f"\nJSON feed written to {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
