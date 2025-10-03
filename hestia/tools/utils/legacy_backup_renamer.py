#!/usr/bin/env python3
import argparse
import datetime
import os
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(".").resolve()

SKIP_DIRS = {
    ".git", ".storage", "_backups/inventory", ".venv", "node_modules",
    "__pycache__", ".mypy_cache", ".ruff_cache"
}
LEGACY_RX = re.compile(r"""
    (\.bak(\b|$|\-|\.\d)|\.perlbak$|_backup(\b|$)|_restore(\b|$))
""", re.IGNORECASE | re.VERBOSE)

def is_skipped(path: pathlib.Path) -> bool:
    # Skip directories listed in SKIP_DIRS
    return any(part in SKIP_DIRS for part in path.parts)

def to_canonical(p: pathlib.Path) -> pathlib.Path:
    utc = (
        datetime.datetime.now(datetime.UTC)
        .strftime("%Y%m%dT%H%M%SZ")
    )
    ext = p.suffix
    # collapse multiple legacy tokens into one .bk.<UTC> before extension
    if ext:
        if not LEGACY_RX.search(p.name):
            name = f"{p.stem}.bk.{utc}{ext}"
        else:
            name = f"{re.sub(LEGACY_RX,'',p.stem)}.bk.{utc}{ext}"
    else:
        name = f"{re.sub(LEGACY_RX,'',p.name)}.bk.{utc}"
    name = name.replace("..", ".").strip(".")
    return p.with_name(name)

def main():
    ap = argparse.ArgumentParser(
        description=(
            "Normalize legacy backup names to *.bk.<UTC> "
            "(dry-run by default)"
        )
    )
    ap.add_argument(
        "--apply", action="store_true", help="perform renames"
    )
    ap.add_argument(
        "--root", default=".",
        help="scan root (default: current repo root)"
    )
    ap.add_argument(
        "--tag", default="",
        help="annotative tag printed in output (no functional effect)"
    )
    args = ap.parse_args()

    changes = []
    root = pathlib.Path(args.root).resolve()
    for d, _, files in os.walk(root):
        dpath = pathlib.Path(d)
        if is_skipped(dpath.relative_to(root)):
            continue
        for f in files:
            p = dpath / f
            if LEGACY_RX.search(p.name):
                dst = to_canonical(p)
                if dst.name != p.name:
                    changes.append((p, dst))
                # If duplicate, handle here (not used in dry-run)
                rels = str(p.relative_to(root))
                reld = str(dst.relative_to(root))
                print(
                    f"FOUND{f'[{args.tag}]' if args.tag else ''}\t"
                    f"{rels} -> {reld}"
                )
    if not args.apply:
        print(f"DRYRUN total={len(changes)}")
        return 0

    # apply
    for src, dst in changes:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            # if content identical, remove src; else append suffix
            if src.read_bytes() == dst.read_bytes():
                src.unlink()
                print(f"DEDUP\t{src}")
            else:
                dup_time = (
                    datetime.datetime.now(datetime.UTC)
                    .strftime("%Y%m%dT%H%M%SZ")
                )
                with_suffix = dst.with_name(
                    dst.stem + ".dup." + dup_time + dst.suffix
                )
                shutil.move(str(src), str(with_suffix))
                print(f"RENAMED_DUP\t{src} -> {with_suffix}")
        else:
            shutil.move(str(src), str(dst))
            print(f"RENAMED\t{src} -> {dst}")
    print(f"APPLY total={len(changes)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())