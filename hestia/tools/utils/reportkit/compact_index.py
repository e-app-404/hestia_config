#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import pathlib
import sys


def sha(s: bytes) -> str: return hashlib.sha256(s).hexdigest()

def main():
    ap = argparse.ArgumentParser(
        description="Compact _backups/inventory/_index.jsonl by age"
    )
    ap.add_argument("--keep-days", type=int, default=30)
    ap.add_argument("--dir", default="_backups/inventory")
    args = ap.parse_args()

    inv = pathlib.Path(args.dir)
    idx = inv / "_index.jsonl"
    arch = inv / "_index.archive.jsonl"

    if not idx.exists():
        print("NOINDEX (nothing to compact)")
        return 0

    cutoff = (
        dt.datetime.now(dt.UTC)
        - dt.timedelta(days=args.keep_days)
    )
    keep, move = [], []

    # Parse index and split lines by age
    with idx.open("rb") as f:
        for line in f:
            try:
                s = line.decode("utf-8", "ignore")
                t = None
                # crude parse: look for 20-char UTC ISO or our UTC stamps
                for token in s.split():
                    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y%m%dT%H%M%SZ"):
                        try:
                            t = dt.datetime.strptime(token, fmt)
                            break
                        except Exception:
                            pass
                    if t:
                        break
                if t and t < cutoff:
                    move.append(line)
                else:
                    keep.append(line)
            except Exception:
                keep.append(line)

    arch_shas = set()
    added = 0

    if arch.exists():
        with arch.open("rb") as f:
            for l in f:
                arch_shas.add(sha(l))

    with arch.open("ab") as f:
        for line in move:
            h = sha(line)
            if h in arch_shas:
                continue
            f.write(line)
            added += 1

    print(
        f"COMPACT keep={len(keep)} moved={len(move)} added_to_archive={added}"
    )

    with idx.open("wb") as f:
        f.writelines(keep)

    return 0

if __name__ == "__main__":
    sys.exit(main())