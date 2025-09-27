"""Verify frontmatter checksums for TSV/CSV/MD files produced by reportkit.

Reads a file with commented frontmatter (lines starting with '# ') and prints a JSON object
with parsed meta and whether the recomputed body SHA256 matches the checksum in the header.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def parse_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(True)
    meta = {}
    body_lines = []
    in_fm = False
    for ln in lines:
        if ln.startswith("# "):
            # strip leading '# ' and split key: value
            kv = ln[2:].strip()
            if kv == "---":
                # toggle
                in_fm = not in_fm
                continue
            if ":" in kv:
                k, v = kv.split(":", 1)
                meta[k.strip()] = v.strip()
            continue
        body_lines.append(ln)
    body = "".join(body_lines)
    h = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return meta, h, body


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    args = p.parse_args(argv)
    path = Path(args.file)
    meta, h, body = parse_frontmatter(path)
    ok = meta.get("checksum_sha256") == h
    out = {"file": str(path), "meta": meta, "body_sha256": h, "match": bool(ok)}
    print(json.dumps(out, ensure_ascii=False, separators=(",",":")))


if __name__ == "__main__":
    main()
