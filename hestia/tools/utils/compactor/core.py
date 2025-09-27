"""Core pure functions for registry compaction.

All functions are pure (no file I/O) and return (new_doc, stats) or other data
structures suitable for unit testing.
"""
from __future__ import annotations

import hashlib
import json
from typing import List, Set, Tuple, FrozenSet


def _bytelen(obj) -> int:
    """Return deterministic compact JSON byte length for obj."""
    return len(json.dumps(obj, ensure_ascii=False, separators=(",",":" )).encode("utf-8"))


def canonicalize(path: str) -> Tuple[dict, int, int, str, str, int]:
    """Load JSON from `path`, re-serialize with compact separators.

    Return (doc, file_bytes, canonical_bytes, sha256_file, sha256_canon, trailing_bytes).
    trailing_bytes is 0 for JSON files that parse fully; included for API parity.
    """
    with open(path, "rb") as fh:
        raw = fh.read()
    file_bytes = len(raw)
    sha_file = hashlib.sha256(raw).hexdigest()
    try:
        doc = json.loads(raw.decode("utf-8"))
    except Exception:
        raise
    canon_bytes = json.dumps(doc, ensure_ascii=False, separators=(",",":" )).encode("utf-8")
    canonical_bytes = len(canon_bytes)
    sha_canon = hashlib.sha256(canon_bytes).hexdigest()
    trailing_bytes = file_bytes - canonical_bytes if file_bytes >= canonical_bytes else 0
    return doc, file_bytes, canonical_bytes, sha_file, sha_canon, trailing_bytes


def sanitize_deleted(doc: dict, keep_last: int = 0) -> Tuple[dict, dict]:
    """Trim or drop data.deleted_entities.

    keep_last=0 => drop all (but keep key as empty list). keep_last>0 => keep N last entries.
    Returns (new_doc, stats).
    """
    # Deep copy via JSON roundtrip (safe and deterministic)
    raw = json.loads(json.dumps(doc, ensure_ascii=False, separators=(",",":" )))
    data = raw.get("data", {})
    de = data.get("deleted_entities")
    before = len(de) if isinstance(de, list) else 0
    if not isinstance(de, list):
        de = []
    if keep_last and keep_last > 0:
        kept = de[-keep_last:]
    else:
        kept = []
    data["deleted_entities"] = kept
    raw["data"] = data
    stats = {
        "deleted_count_before": before,
        "deleted_count_after": len(kept),
        "bytes_saved_est": _bytelen(de) - _bytelen(kept) if isinstance(de, list) else 0,
    }
    return raw, stats


def identify_runtime_duplicates(entities: List[dict], prune_mobile_app: bool = False) -> Set[str]:
    """Return set of entity_ids to remove.

    Heuristics:
    - numbered suffix '_2' and higher: if base entity exists, remove the numbered ones
    - platform clusters: aggressively prune mobile_app if flag set; conservatively ignore other platforms
    """
    by_id = {e.get("entity_id"): e for e in entities if isinstance(e, dict) and e.get("entity_id")}
    remove = set()
    # numbered suffix heuristic
    for eid in list(by_id.keys()):
        if eid is None:
            continue
        if "_" in eid:
            base, _, tail = eid.rpartition("_")
            if tail.isdigit() and base in by_id:
                remove.add(eid)
    # mobile_app clusters
    if prune_mobile_app:
        for e in entities:
            pid = e.get("entity_id")
            plat = e.get("platform") or e.get("platform_name") or e.get("device_class")
            if pid and isinstance(plat, str) and plat.startswith("mobile_app"):
                # prefer to keep the first-seen, drop later ones with same base
                if pid.endswith("_2") or pid.endswith("_3"):
                    remove.add(pid)
    return remove


def compact(
    doc: dict,
    *,
    cap_drop: int = 16384,
    effect_list_max: int = 50,
    opt_trim: int = 0,
    opt_drop: int = 0,
    prune_disabled: FrozenSet[str] = frozenset(),
    prune_duplicates: bool = False,
    prune_mobile_app: bool = False,
    prune_orphaned: bool = False,
) -> Tuple[dict, dict]:
    """Apply pruning & payload compaction and return (new_doc, stats).
    This is a conservative, deterministic compaction implementation.
    """
    raw = json.loads(json.dumps(doc, ensure_ascii=False, separators=(",",":" )))
    data = raw.get("data", {})
    entities = list(data.get("entities", []))
    before_count = len(entities)

    pruned_integration = pruned_device = pruned_user = pruned_duplicates = pruned_orphaned = 0
    capability_entries_touched = effect_lists_emptied = capabilities_dropped = 0
    options_entries_touched = options_dropped = 0

    remove_ids = set()
    if prune_duplicates:
        remove_ids |= identify_runtime_duplicates(entities, prune_mobile_app)

    new_entities = []
    for e in entities:
        eid = e.get("entity_id")
        # prune duplicates
        if eid in remove_ids:
            pruned_duplicates += 1
            continue

        # prune by disabled
        db = e.get("disabled_by")
        if db and db in prune_disabled:
            if db == "integration":
                pruned_integration += 1
            elif db == "device":
                pruned_device += 1
            else:
                pruned_user += 1
            continue

        # prune orphaned
        if prune_orphaned and e.get("orphaned_timestamp"):
            pruned_orphaned += 1
            continue

        # capabilities handling
        caps = e.get("capabilities")
        if isinstance(caps, dict):
            capability_entries_touched += 1
            eff = caps.get("effect_list")
            if isinstance(eff, list):
                if effect_list_max is not None and effect_list_max >= 0 and len(eff) > effect_list_max:
                    # trim
                    caps["effect_list"] = eff[:effect_list_max]
                    effect_lists_emptied += 1
            # drop capabilities entirely if oversized after trim
            if _bytelen(caps) > cap_drop:
                e.pop("capabilities", None)
                capabilities_dropped += 1
            else:
                e["capabilities"] = caps

        # options handling
        opts = e.get("options")
        if isinstance(opts, dict) and opt_trim > 0:
            options_entries_touched += 1
            # trim any list values that are very long
            for k, v in list(opts.items()):
                if isinstance(v, list) and len(v) > opt_trim:
                    opts[k] = v[:opt_trim]
            if _bytelen(opts) > opt_drop and opt_drop > 0:
                e.pop("options", None)
                options_dropped += 1
            else:
                e["options"] = opts

        new_entities.append(e)

    data["entities"] = new_entities
    raw["data"] = data
    after_count = len(new_entities)

    # bytes
    input_bytes = _bytelen(doc)
    output_bytes = _bytelen(raw)
    reduction_pct = round(100.0 * (input_bytes - output_bytes) / max(1, input_bytes), 2)

    stats = {
        "before_entities": before_count,
        "after_entities": after_count,
        "pruned_integration": pruned_integration,
        "pruned_device": pruned_device,
        "pruned_user": pruned_user,
        "pruned_duplicates": pruned_duplicates,
        "pruned_orphaned": pruned_orphaned,
        "capability_entries_touched": capability_entries_touched,
        "effect_lists_emptied": effect_lists_emptied,
        "capabilities_dropped": capabilities_dropped,
        "options_entries_touched": options_entries_touched,
        "options_dropped": options_dropped,
        "input_bytes": input_bytes,
        "output_bytes": output_bytes,
        "reduction_pct": reduction_pct,
        "sanity_key_ok": (raw.get("key") == doc.get("key")),
    }
    return raw, stats


def diff_entities(before: dict, after: dict) -> dict:
    """Return removed and kept entity_ids and small size deltas for capabilities/options."""
    b_entities = {e.get("entity_id"): e for e in (before.get("data", {}).get("entities") or [])}
    a_entities = {e.get("entity_id"): e for e in (after.get("data", {}).get("entities") or [])}
    removed = [eid for eid in b_entities.keys() if eid not in a_entities]
    kept = [eid for eid in a_entities.keys() if eid in b_entities]
    deltas = {}
    for eid in kept:
        be = b_entities.get(eid, {})
        ae = a_entities.get(eid, {})
        caps_before = _bytelen(be.get("capabilities")) if be.get("capabilities") is not None else 0
        caps_after = _bytelen(ae.get("capabilities")) if ae.get("capabilities") is not None else 0
        opts_before = _bytelen(be.get("options")) if be.get("options") is not None else 0
        opts_after = _bytelen(ae.get("options")) if ae.get("options") is not None else 0
        deltas[eid] = {"capabilities_delta": caps_after - caps_before, "options_delta": opts_after - opts_before}
    return {"removed": removed, "kept": kept, "deltas": deltas}
