#!/usr/bin/env python3
import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from jsonschema import validate
from ruamel.yaml import YAML
from tabulate import tabulate

# --- CONSTANTS & NORMALIZATION MAPS ---
EXCL_DIRS = re.compile(r"(?:^|/)(legacy|deprecated|cache|\\.git|\\.venv|\\.storage|backups|node_modules|\\.cloud|\\.idea|\\.vscode|__pycache__)(?:/|$)", re.I)
EXCL_FILES = re.compile(r".*(_legacy|_deprecated|_cache|\\.disabled|\\.example)\\.ya?ml$", re.I)
ALLOWED_EXT = {".yaml", ".yml"}
NAMING_RE = re.compile(r"^[a-z0-9_]+$")
MAX_FILE_SIZE = 5 * 1024 * 1024

ENUM_NORMALIZE = {
    'module': {"zone_tracking": "tracking"},
    'role': {"room_timer": "timer", "zone_tracking": "tracker"},
    'type': {"fallback": "sensor", "presence_state": "sensor", "last_known_zone": "sensor"},
}
LIST_FIELDS = ["upstream_sources", "downstream_consumers", "feeds_from", "feeds_into", "contributes_to", "tags"]
UOM_MAP = {
    'temperature': '°C', 'humidity': '%', 'illuminance': 'lx', 'power': 'W', 'energy': 'kWh',
    'pressure': 'hPa', 'co2': 'ppm', 'volatile_organic_compounds': 'ppb', 'pm25': 'µg/m³', 'signal_strength': 'dBm'
}

# --- ARGPARSE ---
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=str, required=True)
    parser.add_argument("--schema", type=str, required=True)
    parser.add_argument("--reports", type=str, required=True)
    parser.add_argument("--phase-a", action="store_true")
    parser.add_argument("--phase-b", action="store_true")
    parser.add_argument("--phase-b1", action="store_true")
    parser.add_argument("--phase-c", action="store_true")
    parser.add_argument("--phase-dprime", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--apply-normalize", type=str, default="")
    parser.add_argument("--shadow-migration", action="store_true")
    return parser.parse_args()

# --- ENVIRONMENT ASSERTIONS ---
def assert_env(args):
    schema_path = Path(args.schema)
    root = Path(args.root)
    reports_dir = Path(args.reports)
    if not schema_path.exists() or schema_path.stat().st_size < 1024:
        print(f"ERROR: Schema file {schema_path} missing or too small.")
        sys.exit(1)
    yaml_files = [p for p in root.rglob("*.yaml") if p.is_file() and p.stat().st_size < MAX_FILE_SIZE]
    if len(yaml_files) <= 50:
        print(f"ERROR: Only {len(yaml_files)} YAML files found under {root}. Require > 50.")
        sys.exit(1)
    if not reports_dir.exists():
        reports_dir.mkdir(parents=True, exist_ok=True)
    return yaml_files

# --- LOAD SCHEMA ---
def load_schema(schema_path):
    yaml = YAML(typ="safe")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_doc = yaml.load(f)
    schema = schema_doc.get("metadata_schema", {})
    tier_rules = schema_doc.get("tier_rules", {})
    return schema, tier_rules

# --- YAML SCAN ---
def should_skip(p: Path, root: Path):
    rp = str(p.relative_to(root)).replace("\\", "/")
    if p.is_dir():
        m = EXCL_DIRS.search(rp)
        if m:
            return True, f"[{m.group(1)}]"
    else:
        if p.suffix.lower() not in ALLOWED_EXT:
            return True, "[file:ext]"
        if EXCL_FILES.search(p.name):
            return True, f"[file:pattern {p.name}]"
        if p.stat().st_size > MAX_FILE_SIZE:
            return True, "[file:oversize]"
    return False, ""

def scan_yaml(args):
    root = Path(args.root)
    skipped = []
    for dirpath, dirs, files in os.walk(root):
        d = Path(dirpath)
        skip_dir, reason = should_skip(d, root)
        if skip_dir:
            skipped.append((str(d.relative_to(root)), reason or "[unknown]"))
            dirs.clear()
            continue
        for fname in files:
            f = d / fname
            skip_file, reason = should_skip(f, root)
            if skip_file:
                skipped.append((str(f.relative_to(root)), reason or "[unknown]"))
                continue
            yield f
    skip_log = Path(args.reports) / "scan_skipped_paths.txt"
    with open(skip_log, "w", encoding="utf-8") as logf:
        for path, reason in sorted(skipped):
            logf.write(f"{path}\t{reason}\n")

# --- ENTITY EXTRACTION ---
def extract_entities(files_iter, schema):
    yaml = YAML(typ="safe")
    for file_path in files_iter:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.load(f)
        except Exception:
            continue
        for ent, fpath in _extract_entities(data, str(file_path)):
            yield ent, fpath

def _extract_entities(yaml_obj, file_path):
    entities = []
    if isinstance(yaml_obj, dict):
        if "_meta" in yaml_obj or "attributes" in yaml_obj:
            entities.append((yaml_obj, file_path))
        for v in yaml_obj.values():
            entities.extend(_extract_entities(v, file_path))
    elif isinstance(yaml_obj, list):
        for item in yaml_obj:
            entities.extend(_extract_entities(item, file_path))
    return entities

# --- NORMALIZATION (unchanged) ---
def normalize_entity(meta, file_path, entity_id, norm_flags, norm_changes):
    changed = False
    # file
    if "file" not in meta and "file" in norm_flags:
        meta["file"] = str(file_path)
        norm_changes.append((file_path, "file"))
        changed = True
    # canonical_id
    if "canonical_id" not in meta and entity_id and "canonical_id" in norm_flags:
        meta["canonical_id"] = entity_id
        norm_changes.append((file_path, "canonical_id"))
        changed = True
    # lists
    if "lists" in norm_flags:
        for k in LIST_FIELDS:
            v = meta.get(k)
            if isinstance(v, str):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        meta[k] = parsed
                        norm_changes.append((file_path, f"list:{k}"))
                        changed = True
                except Exception:
                    pass
    # enum-basic
    if "enum-basic" in norm_flags:
        for k in ("module", "role", "type"):
            if k in meta and meta[k] in ENUM_NORMALIZE.get(k, {}):
                meta[k] = ENUM_NORMALIZE[k][meta[k]]
                norm_changes.append((file_path, k))
                changed = True
    return meta, changed

# --- VALIDATION (unchanged) ---
def validate_entity(meta, file_path, schema, tier_rules):
    errors = []
    valid = True
    for field, spec in schema.items():
        if spec.get("required") and field not in meta:
            errors.append(f"Missing required field: {field}")
            valid = False
        if "enum" in spec and field in meta:
            if meta[field] not in spec["enum"]:
                errors.append(f"Invalid enum for {field}: {meta[field]}")
                valid = False
    tier = meta.get("tier")
    if tier and tier in tier_rules:
        for req in tier_rules[tier].get("required_fields", []):
            if req not in meta:
                errors.append(f"Tier {tier} missing required: {req}")
                valid = False
    for k in ["area_id", "subarea_id", "container_id"]:
        if k in meta and not NAMING_RE.match(str(meta[k])):
            errors.append(f"{k} fails naming convention: {meta[k]}")
            valid = False
    return valid, errors

# --- REPORT WRITERS ---
def write_report(path, content):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def write_csv(path, rows, headers):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline='', encoding="utf-8") as csvf:
        writer = csv.DictWriter(csvf, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in headers})

# --- PHASES ---
def phase_a(args, schema, tier_rules):
    inventory = []
    norm_changes = []
    key_counter = Counter()
    enum_drift = defaultdict(lambda: defaultdict(list))
    naming_violations = []
    orphaned = []
    files_iter = list(scan_yaml(args))
    entity_count = 0
    for ent, fpath in extract_entities(files_iter, schema):
        meta_raw = ent.get("_meta") or ent.get("attributes")
        meta = dict(meta_raw) if meta_raw else {}
        entity_id = meta.get("entity_id") or meta.get("canonical_id")
        valid, errors = validate_entity(meta, fpath, schema, tier_rules)
        row = {"entity_id": meta.get("canonical_id", ""), "file_path": fpath, **meta, "validation_errors": "; ".join(errors)}
        inventory.append(row)
        entity_count += 1
    # Deterministic sort
    inventory.sort(key=lambda r: (r.get("entity_id", ""), r.get("file_path", "")))
    all_fields = set()
    for row in inventory:
        all_fields.update(row.keys())
    fieldnames = sorted(all_fields)
    write_csv(Path(args.reports) / "inventory.csv", inventory, fieldnames)
    # Markdown
    def section(title, rows):
        return f"\n## {title}\n\n" + (tabulate([list(r.values()) for r in rows], headers=rows[0].keys(), tablefmt="github") if rows else "_None found._")
    md_path = Path(args.reports) / "inventory.md"
    write_report(md_path, "# HESTIA Metadata Inventory\n" + section("Entities with full valid metadata", []) + section("Entities with partial/missing metadata", []) + section("Entities with invalid metadata", inventory))
    # Acceptance
    inv_lines = sum(1 for _ in open(Path(args.reports) / "inventory.csv", encoding="utf-8"))
    md_size = os.stat(md_path).st_size
    print(f"[Phase A] YAML scanned: {len(files_iter)} | Entities: {entity_count}")
    if inv_lines <= 1 or md_size <= 200:
        print(f"Phase A output insufficient. CSV lines: {inv_lines}, MD size: {md_size}")
        sys.exit(1)

def phase_b(args, schema, tier_rules):
    norm_flags = set(args.apply_normalize.split(",")) if args.apply_normalize else set()
    norm_changes = []
    key_counter = Counter()
    enum_drift = defaultdict(lambda: defaultdict(list))
    naming_violations = []
    orphaned = []
    inventory = []
    files_iter = list(scan_yaml(args))
    for ent, fpath in extract_entities(files_iter, schema):
        meta_raw = ent.get("_meta") or ent.get("attributes")
        meta = dict(meta_raw) if meta_raw else {}
        entity_id = meta.get("entity_id") or meta.get("canonical_id")
        meta, changed = normalize_entity(meta, fpath, entity_id, norm_flags, norm_changes)
        for k in meta:
            key_counter[k] += 1
        for k in ["module", "role", "type", "subsystem", "tier"]:
            if k in meta and k in schema and "enum" in schema[k]:
                if meta[k] not in schema[k]["enum"]:
                    enum_drift[k][meta[k]].append(entity_id or fpath)
        for k in ["area_id", "subarea_id", "container_id"]:
            if k in meta and not NAMING_RE.match(str(meta[k])):
                naming_violations.append((entity_id or fpath, k, meta[k]))
        if not meta:
            orphaned.append((fpath, "unknown", "unknown"))
        valid, errors = validate_entity(meta, fpath, schema, tier_rules)
        row = {"entity_id": meta.get("canonical_id", ""), "file_path": fpath, **meta, "validation_errors": "; ".join(errors)}
        inventory.append(row)
    # Write normalization_changes.md
    if norm_changes:
        norm_changes.sort()
        write_report(Path(args.reports) / "normalization_changes.md", "# Normalization Changes (minimal safe apply)\n\n" + tabulate(norm_changes, headers=["file_path", "change"], tablefmt="github"))
    # Write schema_gap_report.md
    write_report(Path(args.reports) / "schema_gap_report.md", "# Schema Gap Report\n\n## Key Frequency Table\n\n" + tabulate(sorted(key_counter.items()), headers=["key", "count"], tablefmt="github") + "\n\n## Enum Drift\n\n" + "\n".join([f"### {k}\n\n" + "\n".join([f"- {val}: {len(ids)} examples (e.g., {ids[:3]})" for val, ids in v.items()]) for k, v in enum_drift.items() if v]) + "\n## Naming Violations\n\n" + (tabulate(naming_violations, headers=["entity_id/file", "field", "offending_value"], tablefmt="github") if naming_violations else "_None found._\n"))
    # Write orphaned_entities.md
    if orphaned:
        orphaned.sort()
        write_report(Path(args.reports) / "orphaned_entities.md", "# Orphaned Entities\n\n" + tabulate(orphaned, headers=["file_path", "domain", "tier"], tablefmt="github"))
    # Write inventory.csv and inventory.md as before
    inventory.sort(key=lambda r: (r.get("entity_id", ""), r.get("file_path", "")))
    all_fields = set()
    for row in inventory:
        all_fields.update(row.keys())
    fieldnames = sorted(all_fields)
    write_csv(Path(args.reports) / "inventory.csv", inventory, fieldnames)
    def section(title, rows):
        return f"\n## {title}\n\n" + (tabulate([list(r.values()) for r in rows], headers=rows[0].keys(), tablefmt="github") if rows else "_None found._")
    write_report(Path(args.reports) / "inventory.md", "# HESTIA Metadata Inventory\n" + section("Entities with full valid metadata", []) + section("Entities with partial/missing metadata", []) + section("Entities with invalid metadata", inventory))


def phase_b1(args, schema, tier_rules):
    inv_path = Path(args.reports) / "inventory.csv"
    if not inv_path.exists():
        print("ERROR: inventory.csv not found. Run Phase B first.")
        sys.exit(1)
    with open(inv_path, newline='', encoding="utf-8") as csvf:
        reader = list(csv.DictReader(csvf))
    canonical_id_map = defaultdict(list)
    b1_rows = []
    for row in reader:
        cid = row.get("canonical_id", "")
        if cid:
            canonical_id_map[cid].append(row)
    for row in reader:
        entity_id = row.get("entity_id", "")
        file_path = row.get("file_path", "")
        tier = row.get("tier", "")
        upstream_sources = row.get("upstream_sources", "")
        try:
            upstream_list = json.loads(upstream_sources) if upstream_sources and upstream_sources.startswith("[") else []
        except Exception:
            upstream_list = []
        device_class = row.get("device_class", "")
        state_class = row.get("state_class", "")
        if tier == "β" and not row.get("alpha_source"):
            rationale = ""
            proposed = ""
            if len(upstream_list) == 1:
                proposed = upstream_list[0]
                rationale = "Single upstream, deterministic"
            elif len(upstream_list) > 1:
                proposed = upstream_list[0]
                rationale = "Multiple upstreams, fallback to first, pending_review"
            else:
                proposed = ""
                rationale = "No upstream_sources"
            b1_rows.append({"entity_id": entity_id, "file_path": file_path, "tier": tier, "proposal_type": "beta_alpha_source", "proposed": proposed, "rationale": rationale})
        if tier == "γ":
            if not row.get("source_entity") and len(upstream_list) == 1:
                b1_rows.append({"entity_id": entity_id, "file_path": file_path, "tier": tier, "proposal_type": "gamma_source_entity", "proposed": upstream_list[0], "rationale": "Single upstream, deterministic"})
            if not row.get("formula_type"):
                b1_rows.append({"entity_id": entity_id, "file_path": file_path, "tier": tier, "proposal_type": "gamma_formula_type", "proposed": "", "rationale": "Missing formula_type, manual author input required"})
        if state_class in {"measurement", "total", "total_increasing"}:
            uom = UOM_MAP.get(device_class, "no deterministic UoM")
            b1_rows.append({"entity_id": entity_id, "file_path": file_path, "tier": tier, "proposal_type": "uom_proposal", "proposed": uom, "rationale": f"device_class: {device_class}"})
    for cid, rows in canonical_id_map.items():
        if len(rows) > 1:
            b1_rows.append({"entity_id": cid, "file_path": ", ".join([r["file_path"] for r in rows]), "tier": ", ".join(set(r["tier"] for r in rows)), "proposal_type": "canonical_id_collision", "proposed": ", ".join([r.get("entity_id","") for r in rows]), "rationale": "Duplicate canonical_id, propose suffixing _1, _2, ..."})
    for row in reader:
        for k in ["module", "role", "type", "subsystem", "tier"]:
            val = row.get(k, "")
            if val and k in schema and "enum" in schema[k] and val not in schema[k]["enum"]:
                b1_rows.append({"entity_id": row.get("entity_id", ""), "file_path": row.get("file_path", ""), "tier": row.get("tier", ""), "proposal_type": f"enum_drift_{k}", "proposed": val, "rationale": "Unknown enum value, recommend normalization or schema expansion"})
    for row in reader:
        for k in ["area_id", "subarea_id", "container_id"]:
            val = row.get(k, "")
            if val and not NAMING_RE.match(str(val)):
                suggested = re.sub(r"[^a-z0-9]+", "_", val.lower())
                b1_rows.append({"entity_id": row.get("entity_id", ""), "file_path": row.get("file_path", ""), "tier": row.get("tier", ""), "proposal_type": f"naming_violation_{k}", "proposed": suggested, "rationale": f"Regex violation: {val}"})
    b1_rows.sort(key=lambda r: (r.get("entity_id", ""), r.get("file_path", "")))
    fieldnames = ["entity_id", "file_path", "tier", "proposal_type", "proposed", "rationale"]
    write_csv(Path(args.reports) / "b1_proposals.csv", b1_rows, fieldnames)
    write_report(Path(args.reports) / "b1_proposals.md", "# Phase B.1 Proposals\n\n" + tabulate(b1_rows, headers="keys", tablefmt="github"))
    print(f"Phase B.1 proposals written to {Path(args.reports) / 'b1_proposals.csv'} and {Path(args.reports) / 'b1_proposals.md'}")

def phase_c(args, schema, tier_rules):
    from collections import defaultdict

    import pandas as pd
    reports_dir = Path(args.reports)
    # Load prior artifacts
    inv_path = reports_dir / "inventory.csv"
    b1_path = reports_dir / "b1_proposals.csv"
    norm_path = reports_dir / "normalization_changes.md"
    orphan_path = reports_dir / "orphaned_entities.md"
    gap_path = reports_dir / "schema_gap_report.md"
    # Load inventory
    inv = pd.read_csv(inv_path) if inv_path.exists() else pd.DataFrame()
    b1 = pd.read_csv(b1_path) if b1_path.exists() else pd.DataFrame()
    # --- 1. Priority fix plan ---
    fix_rows = []
    for _, row in inv.iterrows():
        violations = [v.strip() for v in str(row.get("validation_errors", "")).split(";") if v.strip()]
        tier = row.get("tier", "")
        entity_id = row.get("entity_id", "")
        file_path = row.get("file_path", "")
        # Priority assignment
        priority = "P2"
        if tier in {"ε", "ζ"} or any("Tier " in v and ("ε" in v or "ζ" in v) for v in violations):
            priority = "P0"
        elif tier in {"γ", "β"} or any("Tier " in v and ("γ" in v or "β" in v) for v in violations):
            priority = "P1"
        elif any("Missing required field" in v for v in violations):
            priority = "P0"
        elif any("enum" in v for v in violations):
            priority = "P1"
        fix_rows.append({
            "entity_id": entity_id,
            "file_path": file_path,
            "tier": tier,
            "violations[]": ", ".join(violations),
            "proposed_fix_summary": "; ".join(violations[:2]) if violations else "review",
            "priority": priority
        })
    fix_rows.sort(key=lambda r: (r["priority"], str(r["entity_id"]), str(r["file_path"])))
    fieldnames = ["entity_id", "file_path", "tier", "violations[]", "proposed_fix_summary", "priority"]
    write_csv(reports_dir / "phase_c_fixplan.csv", fix_rows, fieldnames)
    write_report(reports_dir / "phase_c_fixplan.md", "# Phase C: Remediation Plan\n\n" + tabulate(fix_rows, headers="keys", tablefmt="github"))

    # --- 2. Enum normalization map (proposal only) ---
    enum_map = defaultdict(list)
    for _, row in b1.iterrows():
        if row["proposal_type"].startswith("enum_drift_"):
            k = row["proposal_type"].replace("enum_drift_", "")
            enum_map[k].append((row["proposed"], row["entity_id"], row["file_path"]))
    enum_md = ["# Phase C: Enum Normalization Map\n"]
    for k, vals in enum_map.items():
        enum_md.append(f"## {k}\n")
        for val, eid, fpath in sorted((str(val), str(eid), str(fpath)) for val, eid, fpath in vals):
            enum_md.append(f"- `{val}` (entity_id: `{eid}` file: `{fpath}`)")
        enum_md.append("")
    # Seed suggestions
    enum_md.append("\n## Seed Suggestions\n")
    enum_md.append("- role: room_timer→timer; monitor→observer; motion_timeout→delayer; beta_motion→classifier; summary→decorator; formatter→transformer; standardized→transformer")
    enum_md.append("- type: fallback/presence_state/last_known_zone→sensor; delay_proxy→sensor+role=delayer; preference_proxy→sensor+role=controller; logic_sensor/status_proxy/info/status→sensor")
    enum_md.append("- module: motion→tracking; sleep→health; illuminance/room_temperature/rooms/room_merged_sensors→lighting/climate; occupancy→presence")
    write_report(reports_dir / "phase_c_enum_map.md", "\n".join(enum_md))

    # --- 3. Tier remediation cookbook ---
    tier_md = ["# Phase C: Tier Remediation Cookbook\n"]
    tier_md.append("## β\n- Derive alpha_source from single upstream; else mark pending_review.")
    tier_md.append("## γ\n- Require formula_type (author-supplied); propose source_entity when a single upstream exists.")
    tier_md.append("## ε\n- Require threshold + validation_type; explicit fallback.")
    tier_md.append("## ζ\n- Ensure primary_source + fallback_behavior + decision_path.")
    write_report(reports_dir / "phase_c_tier_cookbook.md", "\n".join(tier_md))

    # --- 4. Dry-run diffs (no writes) ---
    dryrun_md = ["# Phase C: Dry-run Diffs (no writes)\n"]
    # Deterministic fixes: enum normalization, β/γ proposals, UoM
    enum_fixes = [r for _, r in b1.iterrows() if r["proposal_type"].startswith("enum_drift_")]
    beta_fixes = [r for _, r in b1.iterrows() if r["proposal_type"] == "beta_alpha_source" and r["proposed"]]
    gamma_fixes = [r for _, r in b1.iterrows() if r["proposal_type"] == "gamma_source_entity" and r["proposed"]]
    uom_fixes = [r for _, r in b1.iterrows() if r["proposal_type"] == "uom_proposal" and r["proposed"]]
    dryrun_md.append(f"## Enum normalization: {len(enum_fixes)} changes\n")
    for r in enum_fixes:
        dryrun_md.append(f"- {r['file_path']}: {r['proposal_type']} → {r['proposed']}")
    dryrun_md.append(f"\n## β alpha_source: {len(beta_fixes)} changes\n")
    for r in beta_fixes:
        dryrun_md.append(f"- {r['file_path']}: set alpha_source = {r['proposed']}")
    dryrun_md.append(f"\n## γ source_entity: {len(gamma_fixes)} changes\n")
    for r in gamma_fixes:
        dryrun_md.append(f"- {r['file_path']}: set source_entity = {r['proposed']}")
    dryrun_md.append(f"\n## UoM: {len(uom_fixes)} changes\n")
    for r in uom_fixes:
        dryrun_md.append(f"- {r['file_path']}: set unit_of_measurement = {r['proposed']}")
    dryrun_md.append(f"\n## Files affected: {len(set(r['file_path'] for r in enum_fixes + beta_fixes + gamma_fixes + uom_fixes))}\n")
    write_report(reports_dir / "phase_c_dryrun_diffs.md", "\n".join(dryrun_md))

    # --- 5. Collision & naming guard ---
    # Canonical ID uniqueness
    canon_map = defaultdict(list)
    for _, row in inv.iterrows():
        cid = row.get("canonical_id", "")
        if cid:
            canon_map[cid].append(row.get("file_path", ""))
    collision_md = ["# Phase C: Canonical ID Collisions\n"]
    for cid, files in canon_map.items():
        if len(files) > 1:
            collision_md.append(f"- {cid}: {files}")
    write_report(reports_dir / "phase_c_canonical_collisions.md", "\n".join(collision_md))
    # Naming violations
    naming_md = ["# Phase C: Naming Violations\n"]
    for _, row in inv.iterrows():
        for k in ["area_id", "subarea_id", "container_id"]:
            val = str(row.get(k, ""))
            if val and not NAMING_RE.match(val):
                naming_md.append(f"- {k}: {val} (entity_id: {row.get('entity_id','')}, file: {row.get('file_path','')})")
    write_report(reports_dir / "phase_c_naming_violations.md", "\n".join(naming_md))

def phase_dprime(args, schema, tier_rules):
    import copy
    from io import StringIO

    reports_dir = Path(args.reports)
    diffs_dir = reports_dir / "phase_dprime_diffs"
    diffs_dir.mkdir(parents=True, exist_ok=True)
    # Scan parity with Phase A
    files_iter = list(scan_yaml(args))
    eligible = []
    skips = []
    dryrun_rows = []
    diff_count = 0
    schema_keys = set(schema.keys())
    for file_path in files_iter:
        yaml = YAML(typ="safe")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                orig_data = yaml.load(f)
        except Exception:
            skips.append({"file_path": str(file_path), "reason": "[unreadable]"})
            continue
        # Helper: find metadata surface
        def find_surface(entity):
            for surfkey in ["_meta", "attributes"]:
                if isinstance(entity, dict) and surfkey in entity and isinstance(entity[surfkey], dict):
                    surf = entity[surfkey]
                    if any(k in schema_keys for k in surf.keys()):
                        return surf, surfkey
            if isinstance(entity, dict):
                for k, v in entity.items():
                    if isinstance(v, dict) and any(sk in v for sk in schema_keys):
                        return v, k
            return None, None
        entities = []
        if isinstance(orig_data, dict):
            for k, v in orig_data.items():
                if isinstance(v, dict):
                    entities.append((k, v))
            if not entities:
                entities = [(None, orig_data)]
        else:
            entities = [(None, orig_data)]
        for ent_key, ent in entities:
            surface, placement = find_surface(ent)
            if not (surface and isinstance(surface, dict)):
                skips.append({"file_path": str(file_path), "reason": "[no-metadata-surface]"})
                continue
            entity_id = ent.get("entity_id")
            unique_id = ent.get("unique_id")
            object_id = ent.get("object_id")
            name = ent.get("name")
            entity_id_str = str(entity_id) if entity_id and str(entity_id).strip().lower() != "nan" else ""
            unique_id_str = str(unique_id) if unique_id and str(unique_id).strip().lower() != "nan" else ""
            object_id_str = str(object_id) if object_id and str(object_id).strip().lower() != "nan" else ""
            name_str = str(name) if name and str(name).strip().lower() != "nan" else ""
            canonical_id = None
            canonical_id_proposed_from = None
            if unique_id_str:
                canonical_id = re.sub(r"[^a-z0-9_]+", "_", unique_id_str.lower())
                canonical_id_proposed_from = "unique_id"
            elif object_id_str:
                canonical_id = re.sub(r"[^a-z0-9_]+", "_", object_id_str.lower())
                canonical_id_proposed_from = "object_id"
            elif name_str:
                canonical_id = re.sub(r"[^a-z0-9_]+", "_", name_str.lower())
                canonical_id = re.sub(r"_+", "_", canonical_id).strip("_")
                canonical_id_proposed_from = "name"
            elif entity_id_str:
                canonical_id = re.sub(r"[^a-z0-9_]+", "_", entity_id_str.lower())
                canonical_id_proposed_from = "entity_id"
            else:
                skips.append({"file_path": str(file_path), "reason": "[no-id-source]"})
                continue
            all_surfaces = []
            for surfkey in ["_meta", "attributes"]:
                if isinstance(ent, dict) and surfkey in ent and isinstance(ent[surfkey], dict):
                    all_surfaces.append(ent[surfkey])
            file_vals = set()
            for surf in all_surfaces:
                if "file" in surf:
                    file_vals.add(str(surf["file"]))
            if len(file_vals) > 1:
                dryrun_rows.append({
                    "file_path": str(file_path),
                    "entity_id": entity_id_str,
                    "tier": surface.get("tier", ""),
                    "placement": placement,
                    "add_canonical_id": False,
                    "add_file": False,
                    "schema_ok": False,
                    "tier_ok": False,
                    "touched_ok": False,
                    "entity_id_str": entity_id_str,
                    "unique_id": unique_id_str,
                    "name": name_str,
                    "canonical_id_proposed_from": canonical_id_proposed_from,
                    "notes": "[conflict:file]"
                })
                continue
            add_canonical_id = "canonical_id" not in surface
            add_file = "file" not in surface
            if not (add_canonical_id or add_file):
                skips.append({"file_path": str(file_path), "reason": "[already-has-canonical_id-and-file]"})
                continue
            def leaf_paths_and_values(obj, prefix=()):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        yield from leaf_paths_and_values(v, prefix + (k,))
                elif isinstance(obj, list):
                    for i, v in enumerate(obj):
                        yield from leaf_paths_and_values(v, prefix + (i,))
                else:
                    yield (prefix, obj)
            orig = orig_data
            sim = copy.deepcopy(orig_data)
            orig_map = dict(leaf_paths_and_values(orig))
            # Find the same entity in the copy
            sim_ent = None
            if ent_key is not None and ent_key in sim:
                sim_ent = sim[ent_key]
            else:
                sim_ent = sim
            sim_surface, _ = find_surface(sim_ent)
            if not (sim_surface and isinstance(sim_surface, dict)):
                skips.append({"file_path": str(file_path), "reason": "[no-metadata-surface-copy]"})
                continue
            # Only insert missing keys
            touched = []
            if add_canonical_id:
                if "canonical_id" not in sim_surface:
                    sim_surface.setdefault("canonical_id", canonical_id)
                    touched.append("canonical_id")
            if add_file:
                if "file" not in sim_surface:
                    sim_surface.setdefault("file", str(file_path))
                    touched.append("file")
            # Check for unexpected deletions or modifications
            sim_map = dict(leaf_paths_and_values(sim))
            unexpected = []
            for p, v in orig_map.items():
                if p not in sim_map:
                    unexpected.append((p, "removed"))
                elif sim_map[p] != v:
                    unexpected.append((p, "modified"))
            if unexpected:
                skips.append({"file_path": str(file_path), "reason": "[unexpected-deletion]", "details": str(unexpected[:5])})
                continue
            # Validation
            schema_ok = True
            tier_ok = True
            try:
                validate(sim_surface, schema)
            except Exception:
                schema_ok = False
            tier = sim_surface.get("tier", "")
            if tier and tier in tier_rules:
                for req in tier_rules[tier].get("required_fields", []):
                    if req not in sim_surface:
                        tier_ok = False
            # touched_ok: both keys present and correct type
            touched_ok = True
            for k in touched:
                if k not in sim_surface or not isinstance(sim_surface[k], (str, int, float)):
                    touched_ok = False
            # Diff (must be only additions)
            orig_buf = StringIO(); yaml.dump(orig, orig_buf); orig_text = orig_buf.getvalue().splitlines(keepends=True)
            new_buf  = StringIO(); yaml.dump(sim,  new_buf ); new_text  = new_buf.getvalue().splitlines(keepends=True)
            import difflib
            diff = list(difflib.unified_diff(orig_text, new_text, fromfile=str(file_path), tofile=str(file_path) + " (dry-run)", n=3))
            if any(line.startswith("-") and not line.startswith("---") for line in diff):
                skips.append({"file_path": str(file_path), "reason": "[unexpected-deletion:diff]"})
                continue
            if touched:
                diff_path = diffs_dir / (Path(file_path).name + ".dryrun.diff")
                with open(diff_path, "w", encoding="utf-8") as df:
                    df.writelines(diff)
                diff_count += 1
            dryrun_rows.append({
                "file_path": str(file_path),
                "entity_id": entity_id_str,
                "tier": sim_surface.get("tier", ""),
                "placement": placement,
                "add_canonical_id": add_canonical_id,
                "add_file": add_file,
                "schema_ok": schema_ok,
                "tier_ok": tier_ok,
                "touched_ok": touched_ok,
                "entity_id_str": entity_id_str,
                "unique_id": unique_id_str,
                "name": name_str,
                "canonical_id_proposed_from": canonical_id_proposed_from,
                "notes": ""
            })
    # Sorting & output
    dryrun_rows.sort(key=lambda r: (r["file_path"], r["entity_id_str"]))
    fieldnames = ["file_path","entity_id","tier","placement","add_canonical_id","add_file","schema_ok","tier_ok","touched_ok","entity_id_str","unique_id","name","canonical_id_proposed_from","notes"]
    write_csv(reports_dir / "phase_dprime_dryrun.csv", dryrun_rows, fieldnames)
    write_report(reports_dir / "phase_dprime_dryrun.md", "# Phase D′ Dry-run Table\n\n" + tabulate(dryrun_rows, headers="keys", tablefmt="github"))
    write_report(reports_dir / "phase_dprime_skips.md", "# Phase D′ Skips\n\n" + tabulate(skips, headers="keys", tablefmt="github"))
    # Summary
    eligible_entities = len(dryrun_rows)
    touched_ok_count = sum(1 for r in dryrun_rows if r["touched_ok"])
    phase_a_count = len(files_iter)
    summary = [
        f"Phase-D′ YAMLs considered = {phase_a_count}",
        f"Eligible entities = {eligible_entities}",
        f"Rows with touched_ok=True = {touched_ok_count}",
        f"Diffs generated = {diff_count}",
        f"Acceptance: {'PASS' if eligible_entities >= 1 and touched_ok_count >= 1 else 'FAIL'}"
    ]
    write_report(reports_dir / "phase_dprime_summary.md", "\n".join(summary))

def phase_d_apply(args, schema, tier_rules):
    import copy
    import difflib
    from io import StringIO
    reports_dir = Path(args.reports)
    patch_root = reports_dir / "phase_d_patches"
    patch_root.mkdir(parents=True, exist_ok=True)
    # Path guards
    ALLOW_PATTERNS = [re.compile(r"/domain/templates/.*\.ya?ml$"), re.compile(r"/packages/.*\.ya?ml$")]
    DENY_PATTERNS = [
        re.compile(r"custom_components/"),
        re.compile(r"hestia/core/"),
        re.compile(r"hestia/core/governance/"),
        re.compile(r"hestia/core/config/")
    ]
    def is_allowed_path(p):
        rel = str(p).replace("\\", "/")
        if any(d.search(rel) for d in DENY_PATTERNS):
            return False
        return any(a.search(rel) for a in ALLOW_PATTERNS)
    # Scan files
    root = Path(args.root)
    files_iter = sorted([p for p in root.rglob("*.yaml") if p.is_file() and p.stat().st_size < MAX_FILE_SIZE])
    changed = []
    failed = []
    skips = []
    summary = []
    def leaf_paths_and_values(obj, prefix=()):
        if isinstance(obj, dict):
            for k, v in obj.items():
                yield from leaf_paths_and_values(v, prefix + (k,))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                yield from leaf_paths_and_values(v, prefix + (i,))
        else:
            yield (prefix, obj)
    schema_keys = set(schema.keys())
    for file_path in files_iter:
        rel_path = str(file_path.relative_to(root)).replace("\\", "/")
        if not is_allowed_path(rel_path):
            skips.append({"file_path": rel_path, "reason": "[out-of-scope]"})
            continue
        yaml = YAML()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                orig_data = yaml.load(f)
        except Exception:
            skips.append({"file_path": rel_path, "reason": "[unreadable]"})
            continue
        # Metadata surface detection
        def find_surface(entity):
            for surfkey in ["_meta", "attributes"]:
                if isinstance(entity, dict) and surfkey in entity and isinstance(entity[surfkey], dict):
                    surf = entity[surfkey]
                    if any(k in schema_keys for k in surf.keys()):
                        return surf, surfkey
            if isinstance(entity, dict):
                for k, v in entity.items():
                    if isinstance(v, dict) and any(sk in v for sk in schema_keys):
                        return v, k
            return None, None
        entities = []
        if isinstance(orig_data, dict):
            for k, v in orig_data.items():
                if isinstance(v, dict):
                    entities.append((k, v))
            if not entities:
                entities = [(None, orig_data)]
        else:
            entities = [(None, orig_data)]
        for ent_key, ent in entities:
            surface, placement = find_surface(ent)
            if not (surface and isinstance(surface, dict)):
                skips.append({"file_path": rel_path, "reason": "[no-metadata-surface]"})
                continue
            entity_id = ent.get("entity_id")
            unique_id = ent.get("unique_id")
            object_id = ent.get("object_id")
            name = ent.get("name")
            entity_id_str = str(entity_id) if entity_id and str(entity_id).strip().lower() != "nan" else ""
            unique_id_str = str(unique_id) if unique_id and str(unique_id).strip().lower() != "nan" else ""
            object_id_str = str(object_id) if object_id and str(object_id).strip().lower() != "nan" else ""
            name_str = str(name) if name and str(name).strip().lower() != "nan" else ""
            canonical_id = None
            canonical_id_proposed_from = None
            if entity_id_str:
                canonical_id = entity_id_str
                canonical_id_proposed_from = "entity_id"
            elif unique_id_str:
                canonical_id = re.sub(r"[^a-z0-9_]+", "_", unique_id_str.lower())
                canonical_id_proposed_from = "unique_id"
            elif object_id_str:
                canonical_id = re.sub(r"[^a-z0-9_]+", "_", object_id_str.lower())
                canonical_id_proposed_from = "object_id"
            elif name_str:
                canonical_id = re.sub(r"[^a-z0-9_]+", "_", name_str.lower())
                canonical_id = re.sub(r"_+", "_", canonical_id).strip("_")
                canonical_id_proposed_from = "name"
            else:
                skips.append({"file_path": rel_path, "reason": "[no-id-source]"})
                continue
            all_surfaces = []
            for surfkey in ["_meta", "attributes"]:
                if isinstance(ent, dict) and surfkey in ent and isinstance(ent[surfkey], dict):
                    all_surfaces.append(ent[surfkey])
            file_vals = set()
            for surf in all_surfaces:
                if "file" in surf:
                    file_vals.add(str(surf["file"]))
            if len(file_vals) > 1:
                skips.append({"file_path": rel_path, "reason": "[conflict:file]"})
                continue
            add_canonical_id = "canonical_id" not in surface
            add_file = "file" not in surface
            if not (add_canonical_id or add_file):
                continue
            orig = orig_data
            sim = copy.deepcopy(orig_data)
            orig_map = dict(leaf_paths_and_values(orig))
            # Find the same entity in the copy
            sim_ent = None
            if ent_key is not None and ent_key in sim:
                sim_ent = sim[ent_key]
            else:
                sim_ent = sim
            sim_surface, _ = find_surface(sim_ent)
            if not (sim_surface and isinstance(sim_surface, dict)):
                skips.append({"file_path": rel_path, "reason": "[no-metadata-surface-copy]"})
                continue
            touched = []
            if add_canonical_id:
                if "canonical_id" not in sim_surface:
                    sim_surface.setdefault("canonical_id", canonical_id)
                    touched.append("canonical_id")
            if add_file:
                if "file" not in sim_surface:
                    sim_surface.setdefault("file", str(file_path))
                    touched.append("file")
            sim_map = dict(leaf_paths_and_values(sim))
            unexpected = []
            for p, v in orig_map.items():
                if p not in sim_map:
                    unexpected.append((p, "removed"))
                elif sim_map[p] != v:
                    unexpected.append((p, "modified"))
            if unexpected:
                skips.append({"file_path": rel_path, "reason": "[unexpected-deletion]", "details": str(unexpected[:5])})
                continue
            # touched_ok: both keys present and correct type
            touched_ok = True
            for k in touched:
                if k not in sim_surface or not isinstance(sim_surface[k], (str, int, float)):
                    touched_ok = False
            # Diff (must be only additions)
            orig_buf = StringIO(); yaml.dump(orig, orig_buf); orig_text = orig_buf.getvalue().splitlines(keepends=True)
            new_buf  = StringIO(); yaml.dump(sim,  new_buf ); new_text  = new_buf.getvalue().splitlines(keepends=True)
            diff = list(difflib.unified_diff(orig_text, new_text, fromfile=rel_path, tofile=rel_path + " (applied)", n=3))
            if any(line.startswith("-") and not line.startswith("---") for line in diff):
                skips.append({"file_path": rel_path, "reason": "[unexpected-deletion:diff]"})
                continue
            if touched_ok:
                # Write file (ruamel round-trip)
                with open(file_path, "w", encoding="utf-8") as wf:
                    yaml.dump(sim, wf)
                # Write patch diff
                patch_path = patch_root / (rel_path.replace("/", "_") + ".patch.diff")
                patch_path.parent.mkdir(parents=True, exist_ok=True)
                with open(patch_path, "w", encoding="utf-8") as pf:
                    pf.writelines(diff)
                changed.append({
                    "file_path": rel_path,
                    "entity_id": entity_id_str,
                    "touched": ",".join(touched),
                    "canonical_id_proposed_from": canonical_id_proposed_from,
                    "notes": ""
                })
            else:
                failed.append({
                    "file_path": rel_path,
                    "entity_id": entity_id_str,
                    "touched": ",".join(touched),
                    "canonical_id_proposed_from": canonical_id_proposed_from,
                    "notes": "[touched_ok=False]"
                })
    # Reports
    changed.sort(key=lambda r: (r["file_path"], r["entity_id"]))
    failed.sort(key=lambda r: (r["file_path"], r["entity_id"]))
    skips.sort(key=lambda r: (r["file_path"],))
    def write_report(path, content):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    def write_csv(path, rows, headers):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline='', encoding="utf-8") as csvf:
            writer = csv.DictWriter(csvf, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in headers})
    write_report(reports_dir / "phase_d_apply_summary.md", f"# Phase D Apply Summary\n\nFiles changed: {len(changed)}\nEntities updated: {sum(1 for _ in changed)}\nSkipped: {len(skips)}\nFailed: {len(failed)}\n\n")
    write_csv(reports_dir / "phase_d_apply_changes.md", changed, ["file_path","entity_id","touched","canonical_id_proposed_from","notes"])
    write_csv(reports_dir / "phase_d_failed_validations.md", failed, ["file_path","entity_id","touched","canonical_id_proposed_from","notes"])
    write_csv(reports_dir / "phase_d_skips.md", skips, ["file_path","reason","details"])
    # Acceptance
    acceptance = (len(changed) >= 1 and all(r["touched"] for r in changed) and not any(s["reason"].startswith("[unexpected-deletion") for s in skips))
    if not acceptance:
        print("[Phase D] No qualifying entities or unexpected deletions detected. No files written.")
    else:
        print(f"[Phase D] Files changed: {len(changed)} | Entities updated: {sum(1 for _ in changed)}")
        print("[Phase D] Head of phase_d_apply_summary.md:")
        with open(reports_dir / "phase_d_apply_summary.md", "r", encoding="utf-8") as f:
            for _ in range(10):
                line = f.readline()
                if not line: break
                print(line.rstrip())
        print("\nReview all diffs in /config/hestia/config/diagnostics/reports/phase_d_patches/ and run:")
        print("  pre-commit run --all-files\n  make validate\n  git show --stat\n")

# --- MAIN ---
def main():
    args = parse_args()
    yaml_files = assert_env(args)
    schema, tier_rules = load_schema(args.schema)
    # Mutually exclusive D apply/dry-run
    if getattr(args, 'phase_d', False):
        if args.dry_run and getattr(args, 'apply', False):
            print("ERROR: --dry-run and --apply are mutually exclusive for Phase D.")
            sys.exit(1)
        if getattr(args, 'apply', False):
            phase_d_apply(args, schema, tier_rules)
            return
    phases = [
        (args.phase_a, phase_a),
        (args.phase_b, phase_b),
        (args.phase_b1, phase_b1),
        (getattr(args, 'phase_c', False), phase_c),
        (getattr(args, 'phase_dprime', False), phase_dprime)
    ]
    for enabled, fn in phases:
        if enabled:
            fn(args, schema, tier_rules)

if __name__ == "__main__":
    main()
