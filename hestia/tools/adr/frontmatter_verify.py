#!/usr/bin/env python3
import pathlib
import sys

import yaml

REQ = {"id", "title", "status", "date"}
ROOT = pathlib.Path("/config/hestia/library/docs/ADR")


def check(p: pathlib.Path):
    s = p.read_text(errors="ignore")
    if not s.startswith("---"):
        return (False, "missing frontmatter fence")
    try:
        block = s.split("---", 2)[1]
        fm = yaml.safe_load(block) or {}
    except Exception as e:
        return (False, f"frontmatter parse error: {e}")
    missing = REQ - set(map(str.lower, fm.keys()))
    return (len(missing) == 0, f"missing: {', '.join(sorted(missing))}" if missing else "ok")


def main():
    paths = sorted(ROOT.glob("ADR-*.md"))
    if not paths:
        print("NO_ADRS")
        return 0
    bad = []
    for p in paths:
        ok, why = check(p)
        print(f"{'OK' if ok else 'FAIL'} {p} {why}")
        if not ok:
            bad.append(p)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
