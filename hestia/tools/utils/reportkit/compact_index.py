#!/usr/bin/env python3
import argparse, datetime as dt, hashlib, os, pathlib, sys

def sha(s: bytes) -> str: return hashlib.sha256(s).hexdigest()

def main():
    ap = argparse.ArgumentParser(description="Compact _backups/inventory/_index.jsonl by age")
    ap.add_argument("--keep-days", type=int, default=30)
    ap.add_argument("--dir", default="_backups/inventory")
    args = ap.parse_args()

    inv = pathlib.Path(args.dir)
    idx = inv / "_index.jsonl"
    arch = inv / "_index.archive.jsonl"

    if not idx.exists():
        print("NOINDEX (nothing to compact)")
        return 0

    cutoff = dt.datetime.utcnow() - dt.timedelta(days=args.keep_days)
    keep, move = [], []

    with idx.open("rb") as f:
        for line in f:
            # best effort: find an ISO timestamp in the line; fallback keep
            try:
                s = line.decode("utf-8", "ignore")
                # crude parse: look for 20-char UTC ISO or our UTC stamps
                t = None
                for token in s.split():
                    token = token.strip().strip('",')
                    for fmt in ("%Y-%m-%dT%H:%M:%SZ","%Y%m%dT%H%M%SZ"):
                        try:
                            t = dt.datetime.strptime(token, fmt)
                            break
                        except: pass
                    if t: break
                if t and t < cutoff:
                    move.append(line)
                else:
                    keep.append(line)
            except Exception:
                keep.append(line)

    # dedup archive by sha
    arch_shas = set()
    if arch.exists():
        with arch.open("rb") as f:
            for l in f:
                arch_shas.add(sha(l))

    added = 0
    if move:
        with arch.open("ab") as f:
            for l in move:
                h = sha(l)
                if h in arch_shas: continue
                f.write(l)
                added += 1
    with idx.open("wb") as f:
        f.writelines(keep)

    print(f"COMPACT keep={len(keep)} moved={len(move)} added_to_archive={added}")
    return 0

if __name__ == "__main__":
    sys.exit(main())