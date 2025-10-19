#!/usr/bin/env python3
# version_id: patch_20251019_02
# artifact: /config/hestia/tools/meta_capture/meta_capture.py

import os, sys, json, uuid, time, shutil, hashlib, argparse, pathlib, glob
from datetime import datetime, timezone

try:
    import tomllib  # py311+
except Exception:
    print("E-RUNTIME-001: Python 3.11+ required (tomllib missing)", file=sys.stderr)
    sys.exit(4)

# Optional deps (graceful degradation)
try:
    import yaml
except Exception:
    yaml = None
try:
    import jsonschema
except Exception:
    jsonschema = None

TOOL_VERSION = os.environ.get("HES_TOOL_VERSION", "1.0.0")
TOML_PATH    = "/config/hestia/config/system/hestia.toml"

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
    # unique + stable order
    return sorted(set(files))

def load_toml_conf() -> dict:
    with open(TOML_PATH, "rb") as f:
        all_cfg = tomllib.load(f)
    mc = all_cfg.get("automation", {}).get("meta_capture", {})
    if not mc:
        print("E-TOML-002: [automation.meta_capture] missing", file=sys.stderr); sys.exit(4)
    return mc

def parse_yaml(text: str):
    if not yaml:
        return None, ["E-RUNTIME-002: PyYAML not available; using heuristic only"]
    try:
        doc = yaml.safe_load(text)
        return doc, []
    except Exception as e:
        return None, [f"E-YAML-DEC-001: {e}"]

def schema_validate(doc, schema_path: str) -> list[str]:
    if not jsonschema or not os.path.exists(schema_path):
        return []
    try:
        schema = json.load(open(schema_path, "r"))
        jsonschema.validate(instance=doc, schema=schema)
        return []
    except Exception as e:
        return [f"E-SCHEMA-001: {e}"]

def load_secret_rules(path: str):
    if not os.path.exists(path):
        return None
    try:
        import re
        rules = yaml.safe_load(open(path, "r")) if yaml else None
        if not rules: return None
        compiled = []
        for pat in (rules.get("patterns") or []):
            rx = re.compile(pat["regex"])
            compiled.append((pat.get("id","E-SECRET"), rx, pat.get("severity","high")))
        entropy = rules.get("entropy_threshold", {"enable": False})
        return {"compiled": compiled, "entropy": entropy}
    except Exception:
        return None

def secrets_scan(text: str, rules) -> list[str]:
    if not rules: return []
    found = []
    for pid, rx, sev in rules.get("compiled", []):
        if rx.search(text):
            found.append(f"{pid}:{sev}")
    # (Optional) entropy check omitted in minimal v1
    return [f"E-SECRET-{i+1}: {hit}" for i, hit in enumerate(found)]

def classify(doc) -> tuple[str, list[str]]:
    errs = []
    if not isinstance(doc, dict):
        return "orange", ["E-SCHEMA-000: root not mapping (heuristic)"]
    required = ["extracted_config","transient_state","relationships","suggested_commands","notes"]
    missing = [k for k in required if k not in doc]
    if missing:
        errs.append(f"E-SCHEMA-010: missing keys {missing}")
        # orange unless schema validator below marks red
        return "orange", errs
    return "green", errs

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

    # prepare
    report_dir.mkdir(parents=True, exist_ok=True)
    index_dir.mkdir(parents=True, exist_ok=True)

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
        doc, parse_errs = parse_yaml(text)
        errors_total.extend([f"{p}: {e}" for e in parse_errs])

        tl_shape, shape_errs = classify(doc if doc is not None else {})
        errors_total.extend([f"{p}: {e}" for e in shape_errs])

        schema_errs = schema_validate(doc if isinstance(doc, dict) else {}, schema_intake)
        errors_total.extend([f"{p}: {e}" for e in schema_errs])

        secret_rules = load_secret_rules(secrets_path)
        secret_errs = secrets_scan(text, secret_rules)
        errors_total.extend([f"{p}: {e}" for e in secret_errs])

        # traffic light decision
        tl = "green"
        if schema_errs or any(e.startswith("E-YAML-DEC") for e in parse_errs) or secret_errs:
            tl = "red"
        elif tl_shape == "orange":
            tl = "orange"

        target = real(config_root / "automation" / f"{pth.stem}.meta.yaml")
        if not within(allowed_root, target):
            errors_total.append(f"{p}: E-ROUTE-ROOT-001 target outside allowed_root")
            tl = "red"

        # apply only if green
        applied = False
        if args.mode == "apply" and tl == "green":
            atomic_write(target, text.encode("utf-8"))
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

    # exit code policy
    red_present = any("E-OVERSIZE" in e or "E-ROUTE-ROOT" in e or "E-FS-404" in e or "E-YAML-DEC" in e or "E-SCHEMA-001" in e or "E-SECRET" in e for e in errors_total)
    if red_present and fail_level == "red":
        sys.exit(3)
    orange_present = any(r["traffic_light"] == "orange" for r in results)
    if (orange_present or red_present) and fail_level == "orange":
        sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
