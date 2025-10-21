#!/usr/bin/env python3
"""
Canonical ADR front-matter verifier (config-driven).

Operational role:
- This is the canonical verifier to plug into the Hestia tool ecosystem.
- It reads adr.toml for dynamic validation rules and emits structured reports.
- Use this tool for capability enhancements; the CI shim `verify_frontmatter.py`
  remains only as a temporary wrapper and will be deprecated.

Outputs:
- Timestamped report: /config/hestia/reports/YYYYMMDD/adr-frontmatter__<ts>__report.log
- Stable latest copy (atomic): /config/hestia/reports/frontmatter-adr.latest.log

Exit codes:
- 0 on success (no errors; warnings allowed)
- 2 on failures (validation errors)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml

# Try stdlib tomllib first (Python 3.11+), then fallback to third-party toml
_toml_loader = None
try:  # Python 3.11+
    import tomllib as _toml_loader  # type: ignore
except Exception:
    try:
        import toml as _toml_loader  # type: ignore
    except Exception as e:  # pragma: no cover
        print(f"ERROR: TOML parser not available (need Python 3.11 tomllib or 'toml' package): {e}")
        sys.exit(1)


THIS = Path(__file__).resolve()
# File is at /config/hestia/tools/adr/frontmatter_verify.py
# parents[0]=.../adr, [1]=.../tools, [2]=.../hestia, [3]=/config
REPO_ROOT = THIS.parents[3]
DEFAULT_ADR_DIR = REPO_ROOT / "hestia" / "library" / "docs" / "ADR"
DEFAULT_CONFIG = REPO_ROOT / "hestia" / "config" / "meta" / "adr.toml"

FRONT_MATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.S)
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ADR_ID_RE = re.compile(r"^ADR-\d{4}$")


@dataclass
class Schema:
    adr_dir: Path
    adr_pattern: str
    required_fields: list[str]
    status_allowed: list[str]
    status_aliases: dict[str, str]
    validation_level: str


def load_schema(config_path: Path, level: str | None) -> Schema:
    cfg = {}
    if config_path.exists():
        try:
            # Prefer tomllib (stdlib) semantics if detected
            if getattr(_toml_loader, "__name__", "") == "tomllib":
                with open(config_path, "rb") as fp:  # tomllib.load requires a binary file object
                    cfg = _toml_loader.load(fp) or {}
            else:
                # Third-party toml can accept a filename or file object
                cfg = _toml_loader.load(str(config_path)) or {}
        except Exception as e:
            print(f"WARN: Failed to parse TOML config at {config_path}: {e}")
            cfg = {}

    files = cfg.get("files", {})
    adr_dir = Path(files.get("adr_directory", str(DEFAULT_ADR_DIR)))
    adr_pattern = files.get("adr_pattern", "ADR-*.md")

    fields = cfg.get("fields", {})
    # Required fields come from fields entries with required=true
    required_fields = [k for k, v in fields.items() if isinstance(v, dict) and v.get("required") is True]

    status = fields.get("status", {})
    status_allowed = status.get("allowed_values", [])
    status_aliases = status.get("deprecated_aliases", {})

    processing = cfg.get("processing", {})
    default_level = "standard"
    if isinstance(processing.get("validation_levels"), dict):
        # If provided, just accept level value; we don't map granular rule sets here
        default_level = "standard"
    validation_level = level or default_level

    return Schema(
        adr_dir=adr_dir,
        adr_pattern=adr_pattern,
        required_fields=required_fields or ["id", "title", "slug", "status", "date", "last_updated"],
        status_allowed=status_allowed or [
            "Draft", "Proposed", "Accepted", "Implemented", "Amended", "Deprecated", "Superseded", "Rejected", "Withdrawn"
        ],
        status_aliases=status_aliases or {"Approved": "Accepted"},
        validation_level=validation_level,
    )


def extract_front_matter(text: str) -> tuple[dict | None, str | None]:
    m = FRONT_MATTER_RE.search(text)
    if not m:
        return None, None
    fm_text = m.group(1)
    try:
        data = yaml.safe_load(fm_text)
        return (data if isinstance(data, dict) else {}), fm_text
    except Exception:
        return {}, fm_text


def is_iso_date(s: str) -> bool:
    if not ISO_DATE_RE.match(s or ""):
        return False
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except Exception:
        return False


def validate_file(
    path: Path,
    text: str,
    fm: dict | None,
    schema: Schema,
    id_to_path: dict[str, Path],
    seen_slugs: dict[str, Path],
) -> list[dict]:
    issues: list[dict] = []
    if fm is None:
        issues.append({"level": "ERROR", "code": "ADR-FM-NO-FRONTMATTER", "path": str(path), "message": "No YAML front-matter found"})
        return issues
    if fm == {}:
        issues.append({"level": "WARN", "code": "ADR-FM-PARSE", "path": str(path), "message": "Front-matter present but not valid YAML"})
        return issues

    # Normalize keys to access
    def getk(k: str):
        # try exact, then case-insensitive
        if k in fm:
            return fm[k]
        for kk in fm:
            if kk.lower() == k.lower():
                return fm[kk]
        return None

    # Required fields
    missing = [k for k in schema.required_fields if getk(k) is None]
    if missing:
        issues.append({
            "level": "ERROR",
            "code": "ADR-FM-MISSING",
            "path": str(path),
            "missing": missing,
            "message": f"Missing required fields: {missing}",
        })

    # ID format and filename alignment
    _id = str(getk("id") or "")
    if _id:
        if not ADR_ID_RE.match(_id):
            issues.append({"level": "ERROR", "code": "ADR-ID-FORMAT", "path": str(path), "message": "ID must match ^ADR-\\d{4}$"})
        # filename consistency
        m = re.match(r"^ADR-(\d{4})", path.name)
        if m and _id != f"ADR-{m.group(1)}":
            issues.append({"level": "ERROR", "code": "ADR-ID-FILENAME-MISMATCH", "path": str(path), "message": "ID must match filename ADR number"})

    # Status allowed / aliases
    status = getk("status")
    if isinstance(status, str):
        if status in schema.status_aliases:
            issues.append({
                "level": "WARN",
                "code": "ADR-STATUS-ALIAS",
                "path": str(path),
                "message": f"Status '{status}' is deprecated; use '{schema.status_aliases[status]}'",
            })
        elif status not in schema.status_allowed:
            issues.append({
                "level": "ERROR",
                "code": "ADR-STATUS-INVALID",
                "path": str(path),
                "message": f"Status must be one of: {schema.status_allowed}",
            })

    # Date fields
    date = getk("date")
    last_updated = getk("last_updated")
    if date is not None and not is_iso_date(str(date)):
        issues.append({"level": "ERROR", "code": "ADR-DATE-FORMAT", "path": str(path), "field": "date", "message": "Date must be YYYY-MM-DD"})
    if last_updated is not None and not is_iso_date(str(last_updated)):
        issues.append({"level": "ERROR", "code": "ADR-DATE-FORMAT", "path": str(path), "field": "last_updated", "message": "Last Updated must be YYYY-MM-DD"})
    if isinstance(date, str) and isinstance(last_updated, str) and is_iso_date(date) and is_iso_date(last_updated):
        if date > last_updated:
            issues.append({"level": "ERROR", "code": "ADR-DATE-CHRONO", "path": str(path), "message": "Creation date cannot be after last_updated"})

    # Title checks (standard: warn on length)
    title = getk("title")
    if isinstance(title, str):
        tlen = len(title.strip())
        if tlen < 15:
            issues.append({"level": "WARN", "code": "ADR-TITLE-SHORT", "path": str(path), "message": "Title should be at least 15 characters"})
        if tlen > 200:
            issues.append({"level": "WARN", "code": "ADR-TITLE-LONG", "path": str(path), "message": "Title should not exceed 200 characters"})
        # Governance update: Title should NOT repeat the ADR id to avoid redundancy.
        # Warn if the title contains the ADR id string.
        if _id and _id in title:
            issues.append({
                "level": "WARN",
                "code": "ADR-TITLE-ID-REDUNDANT",
                "path": str(path),
                "message": "Title should NOT include ADR ID; it's redundant with the id field",
            })

    # Slug checks (regex + uniqueness)
    slug = getk("slug")
    if slug is not None:
        if not isinstance(slug, str) or not re.match(r"^[a-z0-9-]+$", slug):
            issues.append({"level": "ERROR", "code": "ADR-SLUG-FORMAT", "path": str(path), "message": "Slug must be kebab-case (lowercase letters, numbers, hyphens)"})
        else:
            if slug in seen_slugs and seen_slugs[slug] != path:
                issues.append({"level": "ERROR", "code": "ADR-SLUG-DUP", "path": str(path), "message": f"Slug '{slug}' already used by {seen_slugs[slug]}"})
            else:
                seen_slugs[slug] = path

    # Related / Supersedes format + existence (as WARN for now)
    for field in ("related", "supersedes"):
        val = getk(field)
        if val is None:
            continue
        if not isinstance(val, list):
            issues.append({"level": "WARN", "code": "ADR-REL-FORMAT", "path": str(path), "field": field, "message": f"{field} should be an array"})
            continue
        for ref in val:
            if not isinstance(ref, str) or not ADR_ID_RE.match(ref):
                issues.append({"level": "WARN", "code": "ADR-REL-ID-FORMAT", "path": str(path), "field": field, "message": f"Invalid ADR reference '{ref}'"})
            elif ref not in id_to_path:
                issues.append({"level": "WARN", "code": "ADR-REL-NOT-FOUND", "path": str(path), "field": field, "message": f"Referenced ADR '{ref}' not found in workspace"})

    # TOKEN_BLOCK presence (non-fatal)
    if "TOKEN_BLOCK" not in text:
        issues.append({"level": "WARN", "code": "ADR-FM-TOKENBLOCK", "path": str(path), "message": "TOKEN_BLOCK not found in document"})

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Canonical, config-driven ADR front-matter verifier")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to adr.toml configuration")
    parser.add_argument("--adr-dir", default=None, help="Override ADR directory (defaults to config files.adr_directory)")
    parser.add_argument("--level", choices=["basic", "standard", "strict"], default="basic", help="Validation strictness level")
    parser.add_argument("--report", action="store_true", help="Write structured report and index under /config/hestia/reports")
    parser.add_argument("--report-dir", default="/config/hestia/reports", help="Base directory for reports")
    args = parser.parse_args()

    schema = load_schema(Path(args.config), args.level)
    if args.adr_dir:
        schema.adr_dir = Path(args.adr_dir)

    if not schema.adr_dir.exists():
        print(f"ERROR: ADR directory not found: {schema.adr_dir}")
        return 2

    # Discover ADR files (recursive), excluding deprecated/archive
    md_files: list[Path] = [
        p
        for p in schema.adr_dir.rglob(schema.adr_pattern)
        if "/deprecated/" not in str(p) and "/archive/" not in str(p)
    ]
    if not md_files:
        print("No ADR files found; nothing to validate.")
        return 0

    # Preload IDs for cross-reference existence check
    id_to_path: dict[str, Path] = {}
    for p in md_files:
        m = re.match(r"^ADR-\d{4}", p.name)
        if m:
            id_to_path[m.group(0)] = p

    seen_slugs: dict[str, Path] = {}
    failures = 0
    warnings = 0
    issues_all: list[dict] = []

    # Severity mapping based on level: in 'basic', only front-matter presence/parse errors block
    def map_level(level: str, issue: dict) -> str:
        if level == "basic":
            if issue.get("code") in {"ADR-FM-NO-FRONTMATTER"}:
                return "ERROR"
            return "WARN"
        return issue.get("level", "WARN")

    for p in sorted(md_files):
        s = p.read_text(encoding="utf-8", errors="ignore")
        fm, _raw = extract_front_matter(s)
        issues = validate_file(p, s, fm, schema, id_to_path, seen_slugs)
        for it in issues:
            lvl = map_level(schema.validation_level, it)
            if lvl == "ERROR":
                failures += 1
            elif lvl == "WARN":
                warnings += 1
            # Print concise line for humans
            code = it.get("code")
            msg = it.get("message")
            print(f"{lvl}: {code} {p} - {msg}")
        # Store mapped level in report
        for it in issues:
            it["level_effective"] = map_level(schema.validation_level, it)
        issues_all.extend(issues)

    # Reporting
    if args.report:
        ts = datetime.utcnow()
        day_dir = Path(args.report_dir) / ts.strftime("%Y%m%d")
        day_dir.mkdir(parents=True, exist_ok=True)
        tool = "adr-frontmatter"
        report_name = f"{tool}__{ts.strftime('%Y%m%dT%H%M%SZ')}__report.log"
        report_path = day_dir / report_name
        meta = {
            "tool": tool,
            "created_at": ts.isoformat() + "Z",
            "repo_root": str(REPO_ROOT),
            "adr_dir": str(schema.adr_dir),
            "counts": {"errors": failures, "warnings": warnings, "files": len(md_files)},
            "level": schema.validation_level,
            "adr_refs": ["ADR-0009"],
        }
        payload = {"issues": issues_all, "files": [str(p) for p in sorted(md_files)]}
        with report_path.open("w", encoding="utf-8") as fh:
            fh.write("---\n")
            fh.write(json.dumps(meta, indent=2))
            fh.write("\n---\n")
            fh.write(json.dumps(payload, indent=2))
            fh.write("\n")

        # Stable latest copy (atomic replace)
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
        try:
            index_path = Path(args.report_dir) / "_index.jsonl"
            index_line = {"created_at": meta["created_at"], "tool": tool, "path": str(report_path), "counts": meta["counts"], "level": schema.validation_level}
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


if __name__ == "__main__":
    sys.exit(main())
