#!/usr/bin/env python3
import argparse, os, sys, re, json, uuid, time, pathlib
from datetime import datetime, timezone
import yaml  # PyYAML

TOML = "/config/hestia/config/system/hestia.toml"

def nowz():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def read_toml(path=TOML):
    try:
        import tomllib
        with open(path, "rb") as f:
            cfg = tomllib.load(f)
        return cfg.get("automation", {}).get("ha_diagnostics", {})
    except Exception:
        return {}

def ensure_dirs(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)

def atomic_write(path, text):
    p = pathlib.Path(path)
    tmp = p.with_suffix(p.suffix + f".tmp.{int(time.time()*1000)}")
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, p)

def tail_lines(path, n=1000):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return "".join(f.readlines()[-n:])
    except FileNotFoundError:
        return ""

REQUIRED = [
    "/config/home-assistant.log",
    "/config/configuration.yaml",
    "/config/hestia/library/error_patterns.yml",
    "/config/hestia/config/system/maintenance_log.conf",
]

OPTIONAL_GLOBS = [
    "/config/packages/*.yaml",
    "/config/packages/integrations/*.yaml",
    "/config/domain/templates/*.yaml",
    "/config/domain/automations/*.yaml",
    "/config/domain/scripts/*.yaml",
    "/config/domain/command_line/*.yaml",
    "/config/domain/binary_sensors/*.yaml",
    "/config/domain/sensors/*.yaml",
    "/config/domain/sql/*.yaml",
    "/config/.storage/core.entity_registry",
    "/config/.storage/core.device_registry",
    "/config/.storage/core.config_entries",
    "/config/.storage/repairs.issue_registry",
]

def find_patterns(path):
    try:
        data = yaml.safe_load(open(path, "r", encoding="utf-8")) or {}
    except Exception:
        return []
    pats = []
    for item in (data.get("patterns") or []):
        rx = item.get("regex")
        if not rx:
            # fallback to error_format if provided
            rx = item.get("error_format")
        if not rx:
            continue
        try:
            pats.append((re.compile(rx), item.get("id","PATTERN"), item.get("subsystem","other")))
        except re.error:
            continue
    return pats

def classify(log_text, patterns):
    lines = log_text.splitlines()[-500:]
    hits = []
    for ln in lines:
        for rx, pid, subsystem in patterns:
            if rx and rx.search(ln):
                hits.append((ln, pid, subsystem))
                break
    severity = "INFO"
    if any("ERROR" in l for l,_,_ in hits) or any("ERROR" in l for l in lines):
        severity = "ERROR"
    elif any("WARNING" in l for l in lines):
        severity = "WARNING"
    top = hits[0] if hits else (lines[-1] if lines else "", "UNKNOWN", "other")
    component = None
    if top and isinstance(top, tuple) and top[0]:
        m = re.search(r"^(\d{4}-\d{2}-\d{2}.*?)\s+(ERROR|WARNING|INFO)\s+\(([^)]+)\)", top[0])
        if m:
            component = m.group(3)
    return {
        "severity": severity,
        "component": component or "unknown",
        "log_lines": "\n".join(l for l,_,_ in hits[:10]) if hits else "\n".join(lines[-10:])
    }, hits

def smallest_fragment(config_file, key_hint):
    if not os.path.exists(config_file): return ""
    try:
        text = open(config_file, "r", encoding="utf-8").read()
        if not key_hint: return "\n".join(text.splitlines()[:40])
        lines = text.splitlines()
        idx = next((i for i,l in enumerate(lines) if key_hint in l), None)
        if idx is None: return "\n".join(lines[:40])
        start = max(0, idx-10); end = min(len(lines), idx+10)
        return "\n".join(lines[start:end])
    except Exception:
        return ""

def write_report(report_dir, payload, prefix="ha-diagnostics-copilot"):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    path = f"{report_dir}/{prefix}_{ts}.yaml"
    atomic_write(path, yaml.safe_dump(payload, sort_keys=False))
    return path

def write_meta(meta_dir, payload):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    path = f"{meta_dir}/copilot_meta_{ts}.json"
    atomic_write(path, json.dumps(payload, indent=2))
    return path

def run(mode, selection_path, active_file, report_dir, meta_dir):
    ensure_dirs(report_dir, meta_dir)
    missing = [p for p in REQUIRED if not os.path.exists(p)]
    if missing:
        rep = {"missing_required": missing, "mode": mode, "ts": nowz(), "note": "Provide missing artifacts and re-run triage."}
        path = write_report(report_dir, rep)
        write_meta(meta_dir, {"run_id": str(uuid.uuid4()), "mode": mode, "ts": nowz(), "report": path})
        print(path); sys.exit(2)

    log_text = tail_lines("/config/home-assistant.log", 1000)
    patterns = find_patterns("/config/hestia/library/error_patterns.yml")
    classification, hits = classify(log_text, patterns)
    key_hint = None
    if hits:
        m = re.search(r"\b(entity_id|platform|component|integration)[:=]\s*([a-zA-Z0-9_.:-]+)", hits[0][0])
        key_hint = m.group(2) if m else classification.get("component")

    frag = smallest_fragment("/config/configuration.yaml", key_hint or "")
    confidence = 50
    if hits: confidence += 20
    if key_hint: confidence += 10
    if classification["severity"] == "ERROR": confidence += 10
    confidence = max(10, min(95, confidence))

    if mode == "triage":
        report = {
            "evidence": {
                "timestamps": [nowz()],
                "severity": classification["severity"],
                "component": classification["component"],
                "entity": key_hint,
                "log_lines": classification["log_lines"],
                "config_fragment": frag,
            },
            "classification": {
                "subsystem": (hits[0][2] if hits else "other"),
                "probable_severity": "high" if classification["severity"]=="ERROR" else "medium",
                "rationale": "Derived from top matching pattern and adjacent config context."
            },
            "followup": [],
            "CONFIDENCE ASSESSMENT": f"{confidence}%"
        }
        path = write_report(report_dir, report)

    elif mode == "analysis":
        dep = ["configuration.yaml"]
        report = {
            "dependency_chain": dep,
            "root_cause": "Earliest matching log line indicates failing integration or template near the provided fragment.",
            "alternatives_considered": ["Insufficient evidence or multiple candidates in log lines."],
            "comorbidity": ["Cascading template errors can mask original Jinja parse issue."],
            "evidence_lines": classification["log_lines"].splitlines()[:5],
            "CONFIDENCE ASSESSMENT": f"{max(60, confidence)}%"
        }
        path = write_report(report_dir, report)

    elif mode == "remediation":
        if confidence < 80:
            report = {
                "fix_candidates": [],
                "request_evidence": ["Provide the exact config file containing the entity/integration snippet and re-run triage."],
                "CONFIDENCE ASSESSMENT": f"{confidence}%"
            }
            path = write_report(report_dir, report)
        else:
            patch = "# Example patch placeholder; fill with minimal change\n"
            report = {
                "fix_candidates": [{
                    "id": "HA-FIX-001",
                    "description": "Minimal correction based on pattern",
                    "change": patch,
                    "rollback": "git checkout -- <file>",
                    "validation": [
                        {"cmd": "ha core check || hass --script check_config -c /config", "expect": "Configuration valid"}
                    ],
                    "risk": "low",
                    "confidence": confidence
                }],
                "CONFIDENCE ASSESSMENT": f"{confidence}%"
            }
            path = write_report(report_dir, report)
            pathlib.Path(str(path).replace(".yaml","_patch.diff")).write_text(patch, encoding="utf-8")

    else:  # documentation
        report = {
            "documentation": {
                "error_patterns_update": "/config/hestia/library/error_patterns.yml",
                "maintenance_log_update": "/config/hestia/config/system/maintenance_log.conf",
                "adr": "ADR-0008 YAML normalization"
            },
            "next_steps": ["Append validated pattern & maintenance entry"],
            "CONFIDENCE ASSESSMENT": f"{max(60, confidence)}%"
        }
        path = write_report(report_dir, report)

    meta = {
        "run_id": str(uuid.uuid4()),
        "mode": mode,
        "ts": nowz(),
        "report": path,
        "inputs": {"selection_path": selection_path, "active_file": active_file}
    }
    write_meta(meta_dir, meta)
    print(path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["triage","analysis","remediation","documentation"], default="triage")
    ap.add_argument("--selection-path", default=None)
    ap.add_argument("--active-file", default=None)
    ap.add_argument("--report-dir", default=None)
    ap.add_argument("--meta-dir", default=None)
    args = ap.parse_args()

    cfg = read_toml()
    report_dir = args.report_dir or cfg.get("report_dir", "/config/hestia/reports")
    meta_dir   = args.meta_dir   or cfg.get("meta_dir",   "/config/hestia/library/context/meta")
    run(args.mode, args.selection_path, args.active_file, report_dir, meta_dir)

if __name__ == "__main__":
    main()
