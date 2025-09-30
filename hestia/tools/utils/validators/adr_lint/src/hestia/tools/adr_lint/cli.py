"""hestia-adr-lint CLI entrypoint."""
from __future__ import annotations

import argparse
import sys
from typing import List

from . import rules, report, config


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="hestia-adr-lint", description="ADR linter honoring ADR-0009 and ADR-0015")
    p.add_argument("paths", nargs="*", default=["hestia/docs/ADR"], help="Files or directories to check")
    p.add_argument("--format", choices=("human", "json"), default="human", help="Output format")
    p.add_argument("--max-bytes", type=int, default=1048576, help="Max file size in bytes to scan (default 1MB)")
    p.add_argument("--no-follow-symlinks", action="store_true", default=True, help="Do not follow symlinks (default)")
    p.add_argument("--include-playbooks", action="store_true", help="Also lint docs/playbooks and docs/runbooks (operator scope)")
    p.add_argument("--severity-threshold", choices=("warn", "error"), default="error")
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)
    walker_cfg = config.WalkerConfig(max_bytes=args.max_bytes, follow_symlinks=not args.no_follow_symlinks)

    files = rules.collect_targets(args.paths, include_playbooks=args.include_playbooks, walker_cfg=walker_cfg)
    results = [rules.check_file(fp) for fp in files]

    if args.format == 'json':
        print(report.to_json(results))
    else:
        print(report.format(results))

    has_error = any(any(v['severity'] == 'error' for v in r['violations']) for r in results)
    return 1 if has_error else 0


if __name__ == '__main__':
    sys.exit(main())
