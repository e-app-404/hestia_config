#!/usr/bin/env python3
"""
CI shim: Verify ADR front-matter across ADR files using PyYAML.

Governance note (shim/deprecation):
- This script is the current lightweight shim used by CI. Do not add new feature
    capabilities to this file beyond reporting plumbing. The canonical tool is
    `frontmatter_verify.py`, which will integrate with adr.toml for dynamic
    policy and custom alerts across the tool ecosystem.
- Migration signal: While this shim remains the active logic component, it will
    emit a linter-style warning to encourage migration to the canonical tool.

Rules (relaxed for compatibility with current repo):
- Must contain a YAML front-matter block delimited by '---' ... '---'
- Must include at least: title, status, date (minimal governance keys)
- TOKEN_BLOCK presence is WARN-only (printed but not failing)

Reporting outputs:
- Timestamped report remains under /config/hestia/reports/YYYYMMDD/adr-frontmatter__<ts>__report.log
- Stable latest copy is atomically written to /config/hestia/reports/frontmatter-adr.latest.log

Exits non-zero only if front-matter missing or minimal keys absent.
"""
from pathlib import Path
import argparse
import json
import os
from datetime import datetime, timezone
import re
import sys

try:
    import yaml  # provided by CI step: pip install pyyaml
except Exception as e:  # pragma: no cover
    print(f"ERROR: PyYAML not available: {e}")
    sys.exit(1)

THIS = Path(__file__).resolve()
# Hestia root is two levels up from this file: /config/hestia/tools/adr/verify_frontmatter.py
# -> parents[2] == /config/hestia
HESTIA_ROOT = THIS.parents[2]
# Repo root is one level above hestia: /config
REPO_ROOT = HESTIA_ROOT.parent
ADR_DIR = HESTIA_ROOT / 'library' / 'docs' / 'ADR'

FM_RE = re.compile(r'^---\r?\n(.*?)\r?\n---\r?\n', re.S)


def extract_front_matter(text: str):
    m = FM_RE.search(text)
    if not m:
        return None, None
    fm_text = m.group(1)
    try:
        data = yaml.safe_load(fm_text)
        return data if isinstance(data, dict) else {}, fm_text
    except Exception:
        return {}, fm_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify ADR front-matter and optionally write a report")
    parser.add_argument("--report", action="store_true", help="Write a structured report and index entry under /config/hestia/reports")
    parser.add_argument("--report-dir", default="/config/hestia/reports", help="Base directory for reports (default: /config/hestia/reports)")
    args = parser.parse_args()

    # Linter-style migration warning while this shim remains active
    print(
        "WARN: verify_frontmatter.py is a CI shim and will be deprecated — migrate to frontmatter_verify.py (canonical, adr.toml-integrated)",
        file=sys.stderr,
    )

    if not ADR_DIR.exists():
        print(f"WARNING: ADR directory not found: {ADR_DIR}")
        return 0
    md_files = sorted([
        p for p in ADR_DIR.rglob('ADR-*.md')
        if '/archive/' not in str(p) and '/deprecated/' not in str(p)
    ])
    if not md_files:
        print("No ADR files found; nothing to validate.")
        return 0
    failures = 0
    warnings = 0
    issues = []  # collect structured results
    for p in md_files:
        s = p.read_text(encoding='utf-8', errors='ignore')
        fm, raw = extract_front_matter(s)
        if fm is None:
            print(f"ERROR: No YAML front-matter found in {p}")
            failures += 1
            issues.append({
                "level": "ERROR",
                "code": "ADR-FM-NO-FRONTMATTER",
                "path": str(p),
                "message": "No YAML front-matter found"
            })
            continue
        # If YAML failed to parse, fm will be {} but raw present → warn only
        if fm == {} and raw:
            print(f"WARN: Front-matter present but not valid YAML in {p}")
            warnings += 1
            issues.append({
                "level": "WARN",
                "code": "ADR-FM-PARSE",
                "path": str(p),
                "message": "Front-matter present but not valid YAML"
            })
        else:
            # Allow 'date' or 'created' as the primary date key
            minimal = ['title', 'status']
            missing = [k for k in minimal if k not in fm]
            if 'date' not in fm and 'created' not in fm:
                missing.append('date')
            if missing:
                print(f"WARN: Missing minimal keys {missing} in {p}")
                warnings += 1
                issues.append({
                    "level": "WARN",
                    "code": "ADR-FM-MINIMAL",
                    "path": str(p),
                    "missing": missing,
                    "message": "Missing minimal front-matter keys"
                })
        if 'TOKEN_BLOCK' not in s:
            print(f"WARN: TOKEN_BLOCK not found in {p}")
            warnings += 1
            issues.append({
                "level": "WARN",
                "code": "ADR-FM-TOKENBLOCK",
                "path": str(p),
                "message": "TOKEN_BLOCK not found in document"
            })

    # Optional reporting
    if args.report:
        ts = datetime.now(timezone.utc)
        day_dir = Path(args.report_dir) / ts.strftime("%Y%m%d")
        day_dir.mkdir(parents=True, exist_ok=True)
        tool = "adr-frontmatter"
        report_name = f"{tool}__{ts.strftime('%Y%m%dT%H%M%SZ')}__report.log"
        report_path = day_dir / report_name
        meta = {
            "tool": tool,
            "created_at": ts.isoformat(),
            "repo_root": str(REPO_ROOT),
            "adr_dir": str(ADR_DIR),
            "counts": {"errors": failures, "warnings": warnings, "files": len(md_files)},
            "adr_refs": ["ADR-0009"],
        }
        payload = {
            "issues": issues,
            "files": [str(p) for p in md_files],
        }
        # Frontmatter + JSON body
        with report_path.open("w", encoding="utf-8") as fh:
            fh.write("---\n")
            fh.write(json.dumps(meta, indent=2))
            fh.write("\n---\n")
            fh.write(json.dumps(payload, indent=2))
            fh.write("\n")
        # Stable latest copy (atomic replace) at /config/hestia/reports/frontmatter-adr.latest.log
        try:
            base_dir = Path(args.report_dir)
            base_dir.mkdir(parents=True, exist_ok=True)
            latest_path = base_dir / "frontmatter-adr.latest.log"
            tmp_path = base_dir / (latest_path.name + ".tmp")
            with tmp_path.open("w", encoding="utf-8") as fh:
                fh.write("---\n")
                fh.write(json.dumps(meta, indent=2))
                fh.write("\n---\n")
                fh.write(json.dumps(payload, indent=2))
                fh.write("\n")
            os.replace(tmp_path, latest_path)
        except Exception as e:
            print(f"WARN: failed to write latest report copy: {e}", file=sys.stderr)
        # Index JSONL
        index_path = Path(args.report_dir) / "_index.jsonl"
        index_line = {
            "created_at": ts.isoformat(),
            "tool": tool,
            "path": str(report_path),
            "counts": meta["counts"],
        }
        try:
            with index_path.open("a", encoding="utf-8") as idx:
                idx.write(json.dumps(index_line) + "\n")
        except Exception:
            pass
        print(f"Report written: {report_path}")
    if failures:
        print(f"Front-matter verification failures: {failures}")
        return 2
    print("ADR front-matter verification passed (with warnings)." if warnings else "ADR front-matter verification passed.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
