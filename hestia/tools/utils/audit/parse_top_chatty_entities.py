#!/usr/bin/env python3
"""
parse_top_chatty_entities.py

Stream-parse a Home Assistant home-assistant.log and emit "top chatty"
entities and services as TSV files. Hardened to avoid false positives
(module names, IP fragments, version numbers) by:
  - strict entity_id domain whitelist,
  - explicit service-call patterns,
  - per-line de-duplication,
  - deterministic output.

No external dependencies. Python 3.10+.
"""

from __future__ import annotations

import argparse
import gzip
import os
import re
import sys
from collections import Counter
from typing import Iterable, TextIO

# Whitelist of common HA entity domains. Extend if you need more.
ALLOWED_DOMAINS = {
    "binary_sensor","sensor","switch","light","automation","script","scene","climate",
    "media_player","lock","cover","vacuum","camera","button","input_boolean","input_number",
    "input_select","input_text","input_datetime","person","device_tracker","alarm_control_panel",
    "humidifier","fan","remote","timer","counter","number","select","text","update","weather",
    "water_heater","image","image_processing","event","zone"
}

# Regex to capture entity_id=<domain>.<object_id> when written explicitly in JSON-like logs
RE_ENTITY_KV = re.compile(
    r'entity_id["\']?\s*[:=]\s*["\']([a-z_]+)\.([a-zA-Z0-9_]+)["\']'
)

# Regex to capture entity_id patterns in free text, guarded by domain whitelist and word boundaries.
RE_ENTITY_FREE = re.compile(
    r'\b(' + "|".join(sorted(ALLOWED_DOMAINS)) + r')\.([a-zA-Z0-9_]+)\b'
)

# Service-call patterns commonly seen in logs
RE_SERVICE_A = re.compile(r'Calling service\s+([a-z_]+)\.([a-z_]+)\b')
RE_SERVICE_B = re.compile(r'Service call(?: from .*?)?:\s+([a-z_]+)\.([a-z_]+)\b')
RE_SERVICE_C = re.compile(r'Executing service:\s+([a-z_]+)\.([a-z_]+)\b')
RE_SERVICE_D = re.compile(r'async_call[^:]*:\s+([a-z_]+)\.([a-z_]+)\b')

# Exclude IPv4-looking tokens defensively
RE_IPV4 = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

def open_log(path: str) -> TextIO:
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="ignore")
    return open(path, "r", encoding="utf-8", errors="ignore")

def parse_lines(lines: Iterable[str]) -> tuple[Counter, Counter]:
    entities = Counter()
    services = Counter()

    for line in lines:
        # Skip obvious non-signal lines (optional micro-filter, cheap)
        if "homeassistant.loader" in line and "Loaded" in line:
            continue

        line_entities = set()
        line_services = set()

        # 1) Entity IDs explicitly named in JSON-like kv pairs
        for m in RE_ENTITY_KV.finditer(line):
            domain, obj = m.group(1), m.group(2)
            if domain in ALLOWED_DOMAINS:
                token = f"{domain}.{obj}"
                # rudimentary IPv4 guard (object like 192.168.0.1)
                if not RE_IPV4.fullmatch(obj):
                    line_entities.add(token)

        # 2) Entity IDs in free text
        for m in RE_ENTITY_FREE.finditer(line):
            domain, obj = m.group(1), m.group(2)
            token = f"{domain}.{obj}"
            if not RE_IPV4.fullmatch(obj):
                line_entities.add(token)

        # 3) Services
        for rex in (RE_SERVICE_A, RE_SERVICE_B, RE_SERVICE_C, RE_SERVICE_D):
            for m in rex.finditer(line):
                sd, sv = m.group(1), m.group(2)
                # Exclude internal or obvious noise domains if desired:
                # if sd in {"http","system_log"}: continue
                line_services.add(f"{sd}.{sv}")

        # Count once per line per token
        for e in line_entities:
            entities[e] += 1
        for s in line_services:
            services[s] += 1

    return entities, services

def write_tsv(path: str, rows: list[tuple[str, int]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("name\tcount\n")
        for name, count in rows:
            fh.write(f"{name}\t{count}\n")

def write_combined(path: str, ents: list[tuple[str,int]], svcs: list[tuple[str,int]], limit: int) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("type\tname\tcount\n")
        for name, count in ents[:limit]:
            fh.write(f"ENTITY\t{name}\t{count}\n")
        for name, count in svcs[:limit]:
            fh.write(f"SERVICE\t{name}\t{count}\n")

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Extract top chatty entities/services from a Home Assistant log."
    )
    ap.add_argument("--log", default="home-assistant.log", help="Path to home-assistant.log (or .gz)")
    ap.add_argument("--out-dir", default="hestia/ops/audit", help="Output directory for TSVs")
    ap.add_argument("--limit", type=int, default=50, help="Top N rows per table")
    args = ap.parse_args()

    try:
        with open_log(args.log) as fh:
            entities, services = parse_lines(fh)
    except FileNotFoundError:
        print(f"ERROR: log not found: {args.log}", file=sys.stderr)
        return 4
    except Exception as e:
        print(f"ERROR: failed to parse log: {e}", file=sys.stderr)
        return 3

    top_entities = entities.most_common(args.limit)
    top_services = services.most_common(args.limit)

    # Write separate TSVs and a combined quick-look TSV
    write_tsv(os.path.join(args.out_dir, "top_entities.tsv"), top_entities)
    write_tsv(os.path.join(args.out_dir, "top_services.tsv"), top_services)
    write_combined(os.path.join(args.out_dir, "top_chatty.tsv"), top_entities, top_services, args.limit)

    # Print compact JSON summary to stderr (single line)
    summary = {
        "log": args.log,
        "out_dir": args.out_dir,
        "entities_total": len(entities),
        "services_total": len(services),
        "top_limit": args.limit
    }
    import json
    print(json.dumps(summary, separators=(",",":")), file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
