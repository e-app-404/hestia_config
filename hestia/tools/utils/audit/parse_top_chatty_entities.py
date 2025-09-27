"""Example script: parse a log and write top_entities.tsv and top_services.tsv using reportkit."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from hestia.tools.utils.reportkit.reportkit import (
    append_manifest,
    new_batch_dir,
    utc_now_id,
    write_tsv_with_frontmatter,
)


def _body_checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_log(path: Path, limit: int = 50):
    # naive parser: count occurrences of service names (word after 'service:') and entity ids (sensor.*)
    svc = Counter()
    ent = Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        if "service:" in line:
            # crude split
            parts = line.split("service:")
            if len(parts) > 1:
                svcname = parts[1].strip().split()[0]
                svc[svcname] += 1
        # find sensor-like tokens
        for tok in line.split():
            if tok.startswith("sensor.") or tok.startswith("switch."):
                ent[tok] += 1
    return ent.most_common(limit), svc.most_common(limit)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--log", default="sample_home-assistant.log")
    p.add_argument("--reports-dir", default="hestia/reports")
    p.add_argument("--tool", default="audit")
    p.add_argument("--label", default="chatty")
    p.add_argument("--purpose", default="diagnostic")
    p.add_argument("--limit", type=int, default=50)
    args = p.parse_args(argv)

    when = utc_now_id()
    batch = new_batch_dir(args.reports_dir, args.tool, args.label, when)
    batch_id = Path(batch).name

    ent_top, svc_top = parse_log(Path(args.log), args.limit)

    # prepare rows
    ent_rows = "".join(f"{name}\t{count}\n" for name, count in ent_top)
    svc_rows = "".join(f"{name}\t{count}\n" for name, count in svc_top)

    meta = {
        "meta_schema": "v1",
        "created_at": when,
        "tool": args.tool,
        "script": str(Path("hestia/tools/utils/audit/parse_top_chatty_entities.py")),
        "purpose": args.purpose,
        "batch_id": batch_id,
        "input_path": str(Path(args.log)),
    }

    # write files
    ent_path = Path(batch) / "top_entities.tsv"
    svc_path = Path(batch) / "top_services.tsv"
    write_tsv_with_frontmatter(str(ent_path), meta, "name\tcount", ent_rows)
    write_tsv_with_frontmatter(str(svc_path), meta, "name\tcount", svc_rows)

    # append manifest entries for each file
    rel = Path(batch).relative_to(args.reports_dir)
    ent_meta = dict(meta)
    ent_meta.update({"file_relpath": f"{rel.as_posix()}/top_entities.tsv", "format": "tsv", "rows": int(len(ent_top))})
    append_manifest(ent_meta, base_reports_dir=args.reports_dir)

    svc_meta = dict(meta)
    svc_meta.update({"file_relpath": f"{rel.as_posix()}/top_services.tsv", "format": "tsv", "rows": int(len(svc_top))})
    append_manifest(svc_meta, base_reports_dir=args.reports_dir)

    print(json.dumps({"ok": True, "batch": batch, "files": [str(ent_path), str(svc_path)]}, separators=(",",":")))


if __name__ == "__main__":
    main()
