#!/usr/bin/env python3
# version_id: patch_20251019_03
# artifact: /config/hestia/tools/meta_capture/meta_capture.py

import argparse
import glob
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys
import time
import uuid
from datetime import UTC, datetime

# Required
try:
    import tomllib  # py311+
except Exception:
    print("E-RUNTIME-001: Python 3.11+ required (tomllib missing)", file=sys.stderr)
    sys.exit(4)

# Optional (schema)
try:
    import jsonschema
except Exception:
    jsonschema = None

# YAML libs
try:
    import yaml as pyyaml  # for quick shape checks if needed
except Exception:
    pyyaml = None

# ruamel.yaml for comment/anchor-preserving merges
try:
    from ruamel.yaml import YAML as RuamelYAML
except Exception:
    RuamelYAML = None

TOOL_VERSION = os.environ.get("HES_TOOL_VERSION", "1.0.0")
TOML_PATH    = "/config/hestia/config/system/hestia.toml"
PIN_MARKER   = "# @pin"

def now_utc_z() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def real(p: pathlib.Path) -> pathlib.Path:
    return p.resolve()

def within(root: pathlib.Path, path: pathlib.Path) -> bool:
    root = real(root)
    path = real(path)
    return str(path).startswith(str(root))

def atomic_write(dst: pathlib.Path, data: bytes):
    tmp = dst.with_suffix(dst.suffix + f".tmp.{int(time.time()*1000)}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp, "wb") as f:
        f.write(data)
    if dst.exists():
        bak = dst.with_suffix(dst.suffix + f".bak.{int(time.time())}")
        shutil.copy2(dst, bak)
    os.replace(tmp, dst)

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def list_inputs(patterns: list[str]) -> list[str]:
    files = []
    for pat in patterns:
        files.extend(glob.glob(pat))
    return sorted(set(files))

def load_toml_conf() -> dict:
    with open(TOML_PATH, "rb") as f:
        all_cfg = tomllib.load(f)
    mc = all_cfg.get("automation", {}).get("meta_capture", {})
    if not mc:
        print("E-TOML-002: [automation.meta_capture] missing", file=sys.stderr)
        sys.exit(4)
    return mc

def parse_yaml_quick(text: str):
    """Quick parse for shape check (PyYAML)."""
    if not pyyaml:
        return None, ["E-RUNTIME-002: PyYAML not available; heuristic-only shape checks"]
    try:
        doc = pyyaml.safe_load(text)
        return doc, []
    except Exception as e:
        return None, [f"E-YAML-DEC-001: {e}"]

def schema_validate(doc, schema_path: str) -> list[str]:
    if not jsonschema or not schema_path or not os.path.exists(schema_path):
        return []
    try:
        with open(schema_path, encoding="utf-8") as f:
            schema = json.load(f)
        jsonschema.validate(instance=doc, schema=schema)
        return []
    except Exception as e:
        return [f"E-SCHEMA-001: {e}"]

def load_secret_rules(path: str):
    """
    Load secret scanning rules from YAML:
      allowlist: { mac_address: bool, rfc1918_ip: bool, ... }
      patterns: [ { id, description, regex, severity } ]
      entropy_threshold: { enable: bool, bits_per_char: float, min_length: int }
    """
    if not path or not os.path.exists(path):
        return {"compiled": [], "allowlist": {}, "entropy": {"enable": False}}
    if pyyaml is None:
        return {"compiled": [], "allowlist": {}, "entropy": {"enable": False}}

    with open(path, encoding="utf-8") as f:
        data = pyyaml.safe_load(f) or {}
    allowlist = data.get("allowlist", {}) or {}
    entropy = data.get("entropy_threshold", {"enable": False}) or {"enable": False}

    compiled = []
    for pat in (data.get("patterns") or []):
        rx = re.compile(pat.get("regex"))
        compiled.append({
            "id": pat.get("id", "E-SECRET"),
            "rx": rx,
            "severity": pat.get("severity", "high"),
            "description": pat.get("description", "")
        })
    return {"compiled": compiled, "allowlist": allowlist, "entropy": entropy}

def secrets_scan(text: str, rules) -> list[str]:
    """
    Returns a list of error codes. Entropy scanning is optional.
    Allowlist is currently advisory (kept for future exemptions).
    """
    if not rules:
        return []
    hits = []
    for pat in rules.get("compiled", []):
        if pat["rx"].search(text):
            hits.append(f'{pat["id"]}:{pat["severity"]}')
    # entropy (very conservative)
    ent = rules.get("entropy", {"enable": False})
    if ent.get("enable"):
        bpc = float(ent.get("bits_per_char", 3.5))
        min_len = int(ent.get("min_length", 32))
        pattern = rf"[A-Za-z0-9_\-\.]{{{min_len},}}"
        tokens = re.findall(pattern, text)
        for tok in tokens:
            from math import log2
            alphabet = {c for c in tok}
            p = 1.0 / max(1, len(alphabet))
            est = -sum(p * log2(p) for _ in alphabet)
            if est >= bpc:
                hits.append("E-SECRET-ENTROPY:high")
                break
    return hits

def classify_required_keys(doc) -> tuple[str, list[str]]:
    errs = []
    if not isinstance(doc, dict):
        return "orange", ["E-SCHEMA-000: root not mapping"]
    required = ["extracted_config","transient_state","relationships","suggested_commands","notes"]
    missing = [k for k in required if k not in doc]
    if missing:
        errs.append(f"E-SCHEMA-010: missing keys {missing}")
        return "orange", errs
    return "green", errs

# -------- Pin handling (line-based detection) ----------
_pin_key_regex = re.compile(r"^\s*([A-Za-z0-9_\-]+)\s*:\s*.*#\s*@pin\s*$")

def extract_pinned_keys(original_text: str) -> set[str]:
    pins = set()
    for line in original_text.splitlines():
        m = _pin_key_regex.match(line)
        if m:
            pins.add(m.group(1))
    return pins

def pin_conflicts(original_text: str, new_text: str) -> list[str]:
    """
    Naive pin conflict detector: if a pinned key line exists and the value line
    for that key differs in new text.
    """
    conflicts = []
    pins = extract_pinned_keys(original_text)
    if not pins:
        return conflicts
    def kv_line_map(s: str) -> dict:
        out = {}
        for line in s.splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k = line.split(":",1)[0].strip()
                out.setdefault(k, []).append(line.strip())
        return out
    old_map = kv_line_map(original_text)
    new_map = kv_line_map(new_text)
    for k in pins:
        old_lines = old_map.get(k, [])
        new_lines = new_map.get(k, [])
        if old_lines and new_lines and old_lines[0] != new_lines[0]:
            conflicts.append(f"E-PIN-LOCK-001: key '{k}' is pinned and value changed")
    return conflicts

# -------- Merge (ruamel.yaml round-trip) ----------
def ruamel_yaml():
    if RuamelYAML is None:
        raise RuntimeError("E-RUNTIME-003: ruamel.yaml not available")
    y = RuamelYAML()
    y.preserve_quotes = True
    y.indent(mapping=2, sequence=2, offset=0)
    y.width = 120
    return y

def deep_merge(dst, src):
    """Merge src into dst (recursive for mappings/lists) with best-effort typing."""
    try:
        is_mapping = hasattr(dst, "keys") and hasattr(src, "items")
    except Exception:
        is_mapping = False
    if is_mapping:
        for k, v in src.items():
            if k in dst:
                try:
                    dst[k] = deep_merge(dst[k], v)
                except Exception:
                    dst[k] = v
            else:
                import contextlib
                with contextlib.suppress(Exception):
                    dst[k] = v
        return dst
    # lists or scalars: replace by default (policy could become smarter)
    return src

def merge_yaml_preserving(original_text: str | None, new_text: str) -> str:
    y = ruamel_yaml()
    if original_text is None or not original_text.strip():
        # Format the new_text through ruamel for deterministic style
        data = y.load(new_text)
        from io import StringIO
        buf = StringIO()
        y.dump(data, buf)
        return buf.getvalue()
    # Merge
    orig_doc = y.load(original_text)
    new_doc  = y.load(new_text)
    merged   = deep_merge(orig_doc, new_doc)
    from io import StringIO
    buf = StringIO()
    y.dump(merged, buf)
    return buf.getvalue()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", choices=["dry-run","apply"], default="dry-run")
    ap.add_argument("--inputs", nargs="+", required=True, help="Input YAMLs (globs ok)")
    ap.add_argument("--report", default=None)
    args = ap.parse_args()

    cfg = load_toml_conf()
    repo_root    = real(pathlib.Path(cfg["repo_root"]))
    config_root  = real(pathlib.Path(cfg["config_root"]))
    allowed_root = real(pathlib.Path(cfg.get("allowed_root", "/config/hestia")))
    report_dir   = real(pathlib.Path(cfg["report_dir"]))
    index_dir    = real(pathlib.Path(cfg["index_dir"]))
    jsonl_index  = real(pathlib.Path(cfg.get("paths", {}).get("jsonl_index",
                        str(index_dir / "meta_capture__index.jsonl"))))
    oversize     = int(cfg.get("limits", {}).get("oversize_bytes", 5*1024*1024))
    fail_level   = cfg.get("limits", {}).get("fail_level", "red")
    schema_intake= cfg.get("schemas", {}).get("intake", "")
    secrets_path = cfg.get("secrets", {}).get("rules", "")

    if not within(allowed_root, config_root):
        print("E-ROUTE-ROOT-001: config_root outside allowed_root", file=sys.stderr)
        sys.exit(3)

    files = list_inputs(args.inputs)
    ts = now_utc_z()
    run_id, batch_id = str(uuid.uuid4()), str(uuid.uuid4())

    report_dir.mkdir(parents=True, exist_ok=True)
    index_dir.mkdir(parents=True, exist_ok=True)

    # Preload rules
    secret_rules = load_secret_rules(secrets_path)

    errors_total = []
    results = []

    for p in files:
        pth = pathlib.Path(p)
        if not pth.exists():
            errors_total.append(f"{p}: E-FS-404 not found")
            continue
        if pth.stat().st_size > oversize:
            errors_total.append(f"{p}: E-OVERSIZE-001 > {oversize} bytes")
            continue

        raw = pth.read_bytes()
        shex = sha256_bytes(raw)
        text = raw.decode("utf-8", errors="replace")

        # quick parse + shape
        doc, parse_errs = parse_yaml_quick(text)
        errors_total.extend([f"{p}: {e}" for e in parse_errs])

        tl_shape, shape_errs = classify_required_keys(doc if isinstance(doc, dict) else {})
        errors_total.extend([f"{p}: {e}" for e in shape_errs])

        # schema (required if schema present)
        schema_errs = schema_validate(doc if isinstance(doc, dict) else {}, schema_intake)
        errors_total.extend([f"{p}: {e}" for e in schema_errs])

        # secrets
        secret_errs = secrets_scan(text, secret_rules)
        errors_total.extend([f"{p}: {e}" for e in secret_errs])

        # traffic light
        tl = "green"
        if schema_errs or any(e.startswith("E-YAML-DEC") for e in parse_errs) or secret_errs:
            tl = "red"
        elif tl_shape == "orange":
            tl = "orange"

        target = real(config_root / "automation" / f"{pth.stem}.meta.yaml")
        if not within(allowed_root, target):
            errors_total.append(f"{p}: E-ROUTE-ROOT-001 target outside allowed_root")
            tl = "red"

        # pin conflicts (if target exists)
        pin_errs = []
        existing_text = None
        if target.exists():
            existing_text = target.read_text(encoding="utf-8")
            pin_errs = pin_conflicts(existing_text, text)
            if pin_errs:
                tl = "red"
                errors_total.extend([f"{p}: {e}" for e in pin_errs])

        applied = False
        if args.mode == "apply" and tl == "green":
            try:
                merged_text = merge_yaml_preserving(existing_text, text)
            except Exception as e:
                errors_total.append(f"{p}: E-MERGE-001 {e}")
                # fallback to write-through if ruamel missing (still audited by error)
                merged_text = text
            atomic_write(target, merged_text.encode("utf-8"))
            applied = True

        # Determine skip reason for audit clarity
        skip_reason = None
        if not applied:
            if tl == "red":
                if secret_errs:
                    skip_reason = "secrets"
                elif any(
                    e.startswith(("E-YAML-DEC", "E-SCHEMA-001"))
                    for e in (parse_errs + schema_errs)
                ):
                    skip_reason = "schema"
                elif pin_errs:
                    skip_reason = "pin-lock"
                else:
                    skip_reason = "policy"
            elif tl == "orange":
                skip_reason = "routing-or-shape"

        results.append({
            "source": str(pth),
            "target": str(target),
            "sha256": shex,
            "traffic_light": tl,
            "applied": applied,
            "skip_reason": (None if applied else skip_reason)
        })

    counts = {
        "inputs": len(files),
        "apus": len(results),
        "applied": sum(1 for r in results if r["applied"])
    }
    severity_counts = {
        "green": sum(1 for r in results if r["traffic_light"] == "green"),
        "orange": sum(1 for r in results if r["traffic_light"] == "orange"),
        "red": sum(1 for r in results if r["traffic_light"] == "red"),
    }
    report = {
        "ts": ts,
        "run_id": run_id,
        "batch_id": batch_id,
        "tool_version": TOOL_VERSION,
        "repo_root": str(repo_root),
        "config_root": str(config_root),
        "allowed_root": str(allowed_root),
        "mode": args.mode,
        "counts": counts,
        "severity_counts": severity_counts,
        "results": results,
        "errors": errors_total[:1000],
    }
    rpt_json = json.dumps(report, indent=2)
    if args.report:
        atomic_write(pathlib.Path(args.report), rpt_json.encode("utf-8"))
    else:
        print(rpt_json)

    # ledger append
    line = json.dumps({
        "ts": ts, "run_id": run_id, "batch_id": batch_id, "tool_version": TOOL_VERSION,
        "counts": counts, "severity_counts": severity_counts,
        "status": args.mode, "report_path": args.report or ""
    }) + "\n"
    with open(jsonl_index, "a", encoding="utf-8") as f:
        f.write(line)

    # exit codes
    red_present = any(("E-OVERSIZE" in e) or ("E-ROUTE-ROOT" in e) or ("E-FS-404" in e) or
                      ("E-YAML-DEC" in e) or ("E-SCHEMA-001" in e) or ("E-SECRET" in e) or
                      ("E-PIN-LOCK-001" in e) or ("E-MERGE-001" in e) for e in errors_total)
    if red_present and fail_level == "red":
        sys.exit(3)
    orange_present = any(r["traffic_light"] == "orange" for r in results)
    if (orange_present or red_present) and fail_level == "orange":
        sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
