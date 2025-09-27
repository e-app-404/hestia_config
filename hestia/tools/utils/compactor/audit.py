"""Small audit helpers for registry compactor.

I/O kept minimal; functions write to provided paths.
"""
from __future__ import annotations

import json
from collections import Counter


def _bytelen(obj) -> int:
    import json

    return len(json.dumps(obj, ensure_ascii=False, separators=(",",":" )).encode("utf-8"))


def write_size_profile_md(doc: dict, path_md: str, path_top_tsv: str, top_n: int = 100) -> None:
    """Write a small markdown with per-field byte tallies and a TSV of largest entities."""
    fields = Counter()
    entities = doc.get("data", {}).get("entities", [])
    for e in entities:
        for k, v in e.items():
            fields[k] += _bytelen(v)

    lines = ["# Size profile", "", "Field | bytes", "--- | ---"]
    for k, v in fields.most_common():
        lines.append(f"{k} | {v}")

    with open(path_md, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    # top entities by serialized size
    ent_sizes = []
    for e in entities:
        size = _bytelen(e)
        ent_sizes.append((size, e.get("entity_id"), json.dumps(e, ensure_ascii=False, separators=(",",":" ))))
    ent_sizes.sort(reverse=True)
    with open(path_top_tsv, "w", encoding="utf-8") as fh:
        fh.write("entity_id\tsize\tjson\n")
        for size, eid, j in ent_sizes[:top_n]:
            fh.write(f"{eid}\t{size}\t{j}\n")


def write_deleted_preview_tsv(doc: dict, path_tsv: str, limit: int = 20000) -> None:
    """Write first N deleted_entities to TSV with minimal fields and serialized size."""
    dels = doc.get("data", {}).get("deleted_entities") or []
    with open(path_tsv, "w", encoding="utf-8") as fh:
        fh.write("entity_id\twhen_deleted\tbytes\n")
        for d in dels[:limit]:
            eid = d.get("entity_id") if isinstance(d, dict) else str(d)
            when = d.get("when") if isinstance(d, dict) else ""
            fh.write(f"{eid}\t{when}\t{_bytelen(d)}\n")


def write_entity_list_tsv(doc: dict, path_tsv: str) -> None:
    """Write current entities to TSV with basic fields."""
    entities = doc.get("data", {}).get("entities", [])
    with open(path_tsv, "w", encoding="utf-8") as fh:
        fh.write("entity_id\tplatform\tarea\tdevice_id\n")
        for e in entities:
            eid = e.get("entity_id")
            plat = e.get("platform") or e.get("platform_name") or ""
            area = e.get("area_id") or ""
            did = e.get("device_id") or ""
            fh.write(f"{eid}\t{plat}\t{area}\t{did}\n")
