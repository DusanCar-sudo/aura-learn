"""aura-learn command line."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .episodes import correction_row, default_episodes_dir, iter_episodes, stats


def cmd_export(args: argparse.Namespace) -> int:
    root = Path(args.episodes_dir) if args.episodes_dir else default_episodes_dir()
    episodes = list(iter_episodes(root))
    excluded = set(args.exclude_project or [])
    episodes = [e for e in episodes if e.project_hash not in excluded]

    if args.stats:
        print(json.dumps(stats(episodes), indent=2))
        return 0

    rows = [r for e in episodes if (r := correction_row(e, require_approval=not args.include_unapproved))]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(episodes)} episodes read, {len(rows)} correction rows written to {out}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="aura-learn")
    sub = p.add_subparsers(dest="command", required=True)

    e = sub.add_parser("export", help="episodes -> correction JSONL")
    e.add_argument("--episodes-dir", help="default: $AURA_EPISODES_DIR or ~/.aura/episodes")
    e.add_argument("--out", default="data/corrections.jsonl")
    e.add_argument("--stats", action="store_true", help="print statistics instead of writing rows")
    e.add_argument("--include-unapproved", action="store_true", help="keep escalations the reviewer did not approve")
    e.add_argument("--exclude-project", action="append", metavar="HASH", help="project hash to exclude (repeatable)")
    e.set_defaults(func=cmd_export)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
