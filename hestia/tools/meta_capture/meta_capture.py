#!/usr/bin/env python3
# version_id: patch_20251019_03
# artifact: /config/hestia/tools/meta_capture/meta_capture.py

import os, sys, json, uuid, time, shutil, hashlib, argparse, pathlib, glob, re
from datetime import datetime, timezone

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
    from ruamel.yaml import YAML
except Exception:
    YAML = None

TOOL_VERSION = os.environ.get("HES_TOOL_VERSION", "1.0.0")
TOML_PATH    = "/config/hestia/config/system/hestia.toml"
PIN_MARKER   = "# @pin"

def now_utc_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def real(p: pathlib.Path) -> pathlib.Path:
    return p.resolve()

def within(root: pathlib.Path, path: pathlib.Path) -> bool:
    root = real(root); path = real(path)
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
        print("E-TOML-002: [automation.meta_capture] missing", file=sys.stderr); sys.exit(4)
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
        schema = json.load(open(schema_path, "r"))
        jsonschema.validate(instance=doc, schema=schema)
        return []
    except Exception as e:
        return [f"E-SCHEMA-001: {e}"]

def load_secret_rules(path: str):
    """Rule loader (regex only, minimal)."""
    if not path or not os.path.exists(path):
        return []
    try:
        rules = []
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        # Minimal set of common tokens (keep synced with rules file)
        patterns = [
            (r"(?i)AKIA[0-9A-Z]{16}", "AWS_ACCESS"),
            (r"(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,255}", "GITHUB_TOKEN"),
            (r"(?i)bearer\\s+[A-Za-z0-9._-]{16,}", "BEARER_TOKEN"),
            (r"xox[baprs]-[A-Za-z0-9-]{10,48}", "SLACK_TOKEN"),
            (r"-----BEGIN PRIVATE KEY-----[\\s\\S]+?-----END PRIVATE KEY-----", "PRIVATE_KEY"),
        ]
        for rx, name in patterns:
            rules.append((re.compile(rx), name))
        return rules
    except Exception:
        return []

def secrets_scan(text: str, rules) -> list[str]:
    if not rules:
        return []
    hits = []
    for rx, name in rules:
        if rx.search(text):
            hits.append(f"E-SECRET-{name}")
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
    """Naive pin conflict detector: if a pinned key line exists and the value line for that key differs in new text."""
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
def ruamel_yaml() -> YAML:
    if YAML is None:
        raise RuntimeError("E-RUNTIME-003: ruamel.yaml not available")
    y = YAML()
    y.preserve_quotes = True
    y.indent(mapping=2, sequence=2, offset=0)
    y.width = 120
    return y

def deep_merge(dst, src):
    """Merge src into dst (recursive for mappings/lists)."""
    from collections.abc import Mapping
    if isinstance(dst, Mapping) and isinstance(src, Mapping):
        for k, v in src.items():
            if k in dst:
                dst[k] = deep_merge(dst[k], v)
            else:
                dst[k] = v
        return dst
    # lists: replace by default (policy could become smarter)
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
        print("E-ROUTE-ROOT-001: config_root outside allowed_root", file=sys.stderr); sys.exit(3)

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
            errors_total.append(f"{p}: E-FS-404 not found"); continue
        if pth.stat().st_size > oversize:
            errors_total.append(f"{p}: E-OVERSIZE-001 > {oversize} bytes"); continue

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
                merged_text = text  # fallback to write-through if ruamel missing (still audited by error)
            atomic_write(target, merged_text.encode("utf-8"))
            applied = True

        results.append({
            "source": str(pth),
            "target": str(target),
            "sha256": shex,
            "traffic_light": tl,
            "applied": applied
        })

    counts = {
        "inputs": len(files),
        "apus": len(results),
        "applied": sum(1 for r in results if r["applied"])
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
        "counts": counts, "status": args.mode, "report_path": args.report or ""
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
