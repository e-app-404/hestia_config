"""Retention utility: delete old batches based on manifest entries."""
from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path
from typing import Optional


def _parse_age(s: str) -> datetime.timedelta:
    # support formats like 60d, 3600s, 24h
    if s.endswith("d"):
        return datetime.timedelta(days=int(s[:-1]))
    if s.endswith("h"):
        return datetime.timedelta(hours=int(s[:-1]))
    if s.endswith("m"):
        return datetime.timedelta(minutes=int(s[:-1]))
    if s.endswith("s"):
        return datetime.timedelta(seconds=int(s[:-1]))
    # default days
    return datetime.timedelta(days=int(s))


def load_manifest(base: Path):
    mf = base / "_index.jsonl"
    if not mf.exists():
        return []
    out = []
    with mf.open("r", encoding="utf-8") as fh:
        for line in fh:
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def run(base_dir: str, older_than: str, prefix: Optional[str], tool: Optional[str], dry_run: bool, yes: bool):
    base = Path(base_dir)
    now = datetime.datetime.utcnow()
    ttl = _parse_age(older_than)
    entries = load_manifest(base)
    # group by batch_id
    batches = {}
    for e in entries:
        bid = e.get("batch_id")
        batches.setdefault(bid, []).append(e)

    to_delete = []
    for bid, ens in batches.items():
        # parse created_at
        created = ens[0].get("created_at")
        try:
            dt = datetime.datetime.fromisoformat(created.replace("Z", "+00:00"))
        except Exception:
            continue
        age = now - dt
        if age >= ttl:
            # apply filters
            if prefix and not bid.endswith(prefix):
                continue
            if tool and not any(e.get("tool") == tool for e in ens):
                continue
            to_delete.append((bid, ens))

    summary = {"candidates": len(to_delete)}
    print(json.dumps(summary, separators=(",",":")))
    if dry_run:
        for bid, ens in to_delete:
            print(f"DRY {bid}")
        return
    if not yes:
        print("Refusing to delete without --yes")
        return
    # perform deletion
    for bid, ens in to_delete:
        # find batch dir from file_relpath
        rel = ens[0].get("file_relpath")
        if not rel:
            continue
        batch_dir = base / Path(rel).parts[0] / Path(rel).parts[1]
        if batch_dir.exists() and batch_dir.is_dir():
            try:
                for p in batch_dir.rglob("*"):
                    try:
                        if p.is_file():
                            p.unlink()
                    except Exception:
                        pass
                batch_dir.rmdir()
            except Exception:
                pass


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="hestia/reports")
    p.add_argument("--older-than", required=True)
    p.add_argument("--prefix")
    p.add_argument("--tool")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--yes", action="store_true")
    args = p.parse_args(argv)
    run(args.base, args.older_than, args.prefix, args.tool, args.dry_run, args.yes)


if __name__ == "__main__":
    main()
