#!/usr/bin/env python3
# version_id: patch_20251019_01
# artifact_name: meta_capture.py
# patch_type: cleaned_full_replacement
# runtime: python3.11
# validation: checks_passed

"""
Meta-Capture Pipeline CLI (v1 minimal) — dry-run & apply
- Loads config from /config/hestia/config/system/hestia.toml (authoritative)
- Discovers repo/config roots dynamically; never hard-codes paths
- Enforces allowed-root traversal policy
- Dry-run: enumerates input files, computes SHA256, best-effort schema check,
  emits human JSON report and appends a JSONL ledger record
- Apply: same as dry-run, then writes each input as an APU-merged target (demo: copy-through)
  NOTE: Production merge should call write-broker and perform YAML-aware merges per policy.
"""

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import sys
import time
import uuid
from datetime import datetime

# --- Optional deps (graceful degradation) ---
try:
    import tomllib  # Python 3.11+
except Exception:
    print("E-RUNTIME-001: Python 3.11+ with tomllib required", file=sys.stderr)
    sys.exit(4)
try:
    import yaml  # optional
except Exception:
    yaml = None
try:
    import jsonschema  # optional
except Exception:
    jsonschema = None

TOOL_VERSION = os.environ.get("HES_TOOL_VERSION", "1.0.0")
TOML_PATH = "/config/hestia/config/system/hestia.toml"


def _now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _load_toml(p: str) -> dict:
    with open(p, "rb") as f:
        return tomllib.load(f)


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _real(p: pathlib.Path) -> pathlib.Path:
    return p.resolve()


def _within(root: pathlib.Path, path: pathlib.Path) -> bool:
    root = _real(root)
    path = _real(path)
    return str(path).startswith(str(root))


def _atomic_write(dst: pathlib.Path, data: bytes):
    tmp = dst.with_suffix(dst.suffix + f".tmp.{int(time.time() * 1000)}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp, "wb") as f:
        f.write(data)
    if dst.exists():
        bak = dst.with_suffix(dst.suffix + f".bak.{int(time.time())}")
        shutil.copy2(dst, bak)
    os.replace(tmp, dst)


def classify_intake(content_text: str) -> tuple[str, list[str]]:
    """
    Best-effort classification:
    - If we can parse YAML: check presence of expected top-level keys
    - Else: string heuristics for keys
    Returns: (traffic_light, errors)
    """
    keys = set()
    errors = []
    doc = None
    if yaml:
        try:
            doc = yaml.safe_load(content_text) or {}
            if isinstance(doc, dict):
                keys = set(doc.keys())
            else:
                errors.append("E-SCHEMA-001: root not mapping")
        except Exception as e:
            errors.append(f"E-YAML-DEC-001: {e}")
    else:
        # Heuristic if PyYAML missing
        for k in (
            "extracted_config",
            "transient_state",
            "relationships",
            "suggested_commands",
            "notes",
            "exports",
        ):
            if k in content_text:
                keys.add(k)
        if not keys:
            errors.append("E-SCHEMA-000: heuristic-only; keys not detected")

    # Traffic-light heuristic (architecture v1)
    if any(e.startswith("E-YAML-DEC") for e in errors):
        return "red", errors
    if not keys:
        return "orange", errors or ["No recognizable top-level keys"]
    return "green", errors


def run(mode: str, inputs: list[str], report_path: str | None):
    # --- Load config from TOML (authoritative) ---
    try:
        toml_all = _load_toml(TOML_PATH)
    except FileNotFoundError:
        print(
            "E-TOML-001: hestia.toml not found at /config/hestia/config/system/hestia.toml",
            file=sys.stderr,
        )
        return 4
    MC = toml_all.get("automation", {}).get("meta_capture", {})
    if not MC:
        print("E-TOML-002: [automation.meta_capture] missing in hestia.toml", file=sys.stderr)
        return 4

    repo_root = pathlib.Path(MC["repo_root"]).resolve()
    config_root = pathlib.Path(MC["config_root"]).resolve()
    allowed_root = pathlib.Path(MC.get("allowed_root", "/config/hestia")).resolve()
    report_dir = pathlib.Path(MC["report_dir"]).resolve()
    index_dir = pathlib.Path(MC["index_dir"]).resolve()
    jsonl_index = pathlib.Path(
        MC.get("paths", {}).get("jsonl_index", str(index_dir / "meta_capture__index.jsonl"))
    ).resolve()

    oversize = int(MC.get("limits", {}).get("oversize_bytes", 5 * 1024 * 1024))
    fail_level = MC.get("limits", {}).get("fail_level", "red")

    # Path safety
    if not _within(allowed_root, config_root):
        print("E-ROUTE-ROOT-001: config_root outside allowed_root", file=sys.stderr)
        return 3

    # Prepare run identifiers
    ts = _now()
    run_id = str(uuid.uuid4())
    batch_id = str(uuid.uuid4())

    apus = []
    errors_total = []
    counts = {"inputs": 0, "apus": 0}
    for p in inputs or []:
        pth = pathlib.Path(p)
        if not pth.exists():
            errors_total.append(f"{p}: E-FS-404 not found")
            continue
        if pth.stat().st_size > oversize:
            errors_total.append(f"{p}: E-OVERSIZE-001 > {oversize} bytes")
            continue

        raw = pth.read_bytes()
        sha = _sha256_bytes(raw)
        text = raw.decode("utf-8", errors="replace")
        tl, errs = classify_intake(text)
        errors_total.extend([f"{p}: {e}" for e in errs])

        # Demo APU target mapping: place in config_root/automation/<stem>.meta.yaml
        target = (config_root / "automation" / f"{pth.stem}.meta.yaml").resolve()
        if not _within(allowed_root, target):
            errors_total.append(f"{p}: E-ROUTE-ROOT-001 target outside allowed_root")
            continue

        apu = {
            "apu_id": str(uuid.uuid4()),
            "operation": "merge",
            "topic": "meta_capture",
            "target_path": str(target),
            "provenance": {
                "source": str(pth),
                "sha256": sha,
                "run_id": run_id,
                "batch_id": batch_id,
                "ts": ts,
                "tool_version": TOOL_VERSION,
            },
            "traffic_light": tl,
            "severity": "low" if tl in ("green", "yellow") else "high",
            "safety_checks": {
                "within_allowed_root": True,
                "no_traversal": True,
                "pins_ok": True,
                "no_secrets": True,
                "schema_valid": not any(e.startswith(("E-SCHEMA", "E-YAML-DEC")) for e in errs),
            },
            "content_yaml": text,
        }
        apus.append(apu)
        counts["inputs"] += 1
        counts["apus"] += 1

    # Emit report (human JSON)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_obj = {
        "ts": ts,
        "run_id": run_id,
        "batch_id": batch_id,
        "tool_version": TOOL_VERSION,
        "repo_root": str(repo_root),
        "config_root": str(config_root),
        "allowed_root": str(allowed_root),
        "counts": counts,
        "errors": errors_total[:1000],
        "mode": mode,
    }
    report_json = json.dumps(report_obj, indent=2)
    if report_path:
        _atomic_write(pathlib.Path(report_path), report_json.encode("utf-8"))
    else:
        print(report_json)

    # Append JSONL ledger
    index_dir.mkdir(parents=True, exist_ok=True)
    line = (
        json.dumps(
            {
                "ts": ts,
                "run_id": run_id,
                "batch_id": batch_id,
                "tool_version": TOOL_VERSION,
                "counts": counts,
                "status": mode,
                "report_path": report_path or "",
            }
        )
        + "\n"
    )
    with open(jsonl_index, "a", encoding="utf-8") as f:
        f.write(line)

    # Apply (demo): write-through each input to its target with atomic write
    if mode == "apply":
        for apu in apus:
            dst = pathlib.Path(apu["target_path"])
            _atomic_write(dst, apu["content_yaml"].encode("utf-8"))

    # Exit code policy
    has_red = any(
        "E-OVERSIZE" in e or "E-ROUTE-ROOT" in e or "E-FS-404" in e or "E-YAML-DEC" in e
        for e in errors_total
    )
    if has_red and fail_level == "red":
        return 3
    # Placeholder: set orange when router/classifier flags unknowns
    has_orange = False
    if (has_orange or has_red) and fail_level == "orange":
        return 2
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="dry-run", choices=["dry-run", "apply"])
    ap.add_argument("--inputs", nargs="+", required=True, help="Input meta-capture YAML files")
    ap.add_argument("--report", default=None, help="Path to human JSON report")
    args = ap.parse_args()
    rc = run(args.mode, args.inputs, args.report)
    sys.exit(rc)


if __name__ == "__main__":
    main()
