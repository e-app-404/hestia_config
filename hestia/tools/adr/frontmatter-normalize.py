#!/usr/bin/env python3
"""
ADR front-matter normalizer (config-driven, dry-run by default).

Purpose:
- Apply safe, schema-informed normalizations to ADR front-matter and document body.
- Keep logic modular and adjustable via adr.toml and CLI flags.

Key behaviors by level:
- basic: status alias normalization, related/supersedes cleanup (extract ADR-#### ids),
         no content rewrite beyond front-matter normalization; TOKEN_BLOCK addition is allowed.
- standard: includes basic + slug regeneration (if invalid), ensure TOKEN_BLOCK section present.
- strict: includes standard + optionally prefix ADR ID in title (if missing) and auto-update
last_updated on change.

Reporting:
- Timestamped report under hestia/reports/YYYYMMDD/adr-frontmatter-normalize__<ts>__report.log
- Stable latest copy atomically at hestia/reports/adr-frontmatter-normalize.latest.log

Writes:
- Dry-run unless --apply is set. When applying, uses atomic replace (tmp file + os.replace).

References: ADR-0009, ADR-0024, ADR-0027
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path

import yaml

# TOML loader (tomllib on 3.11+, else toml)
_toml_loader = None
try:
    import tomllib as _toml_loader  # type: ignore
except Exception:
    try:
        import toml as _toml_loader  # type: ignore
    except Exception as e:  # pragma: no cover
        print(f"ERROR: TOML parser not available: {e}")
        raise SystemExit(1) from e


THIS = Path(__file__).resolve()
REPO_ROOT = THIS.parents[3]  # /config
DEFAULT_ADR_DIR = REPO_ROOT / "hestia" / "library" / "docs" / "ADR"
DEFAULT_CONFIG = REPO_ROOT / "hestia" / "config" / "meta" / "adr.toml"

FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.S)
ADR_ID_RE = re.compile(r"^ADR-\d{4}$")
ADR_TOKEN_RE = re.compile(r"ADR-\d{4}")
SLUG_RE = re.compile(r"^[a-z0-9-]+$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load_toml(config_path: Path) -> dict:
    if _toml_loader is None:
        return {}
    if getattr(_toml_loader, "__name__", "") == "tomllib":
        with open(config_path, "rb") as fp:
            return _toml_loader.load(fp) or {}
    # third-party toml
    with open(config_path, encoding="utf-8") as fp:
        return _toml_loader.load(fp) or {}


def extract_front_matter(text: str) -> tuple[dict | None, str | None]:
    m = FM_RE.search(text)
    if not m:
        return None, None
    fm_text = m.group(1)
    try:
        data = yaml.safe_load(fm_text)
        return (data if isinstance(data, dict) else {}), fm_text
    except Exception:
        return {}, fm_text


def kebab(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s


def is_iso_date(s: str) -> bool:
    if not isinstance(s, str) or not ISO_DATE_RE.match(s):
        return False
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except Exception:
        return False


def normalize_related(val) -> list[str]:
    result: list[str] = []
    if val is None:
        return result
    if isinstance(val, list):
        for item in val:
            if isinstance(item, str):
                m = ADR_TOKEN_RE.search(item)
                if m:
                    result.append(m.group(0))
            elif isinstance(item, dict):
                # Use first key that matches ADR-####
                for k in item:
                    if ADR_ID_RE.match(str(k)):
                        result.append(str(k))
                        break
    # Deduplicate preserving order
    seen = set()
    deduped = []
    for x in result:
        if x not in seen:
            seen.add(x)
            deduped.append(x)
    return deduped


def ensure_token_block(text: str) -> tuple[str, bool]:
    if "TOKEN_BLOCK" in text:
        return text, False
    # Append a minimal token block at end with a newline separator
    block = "\n\n## TOKEN_BLOCK\n```yaml\nTOKEN_BLOCK:\n  notes: added by normalizer\n```\n"
    return text + block, True


def atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser(description="ADR front-matter normalizer (dry-run default)")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to adr.toml config")
    parser.add_argument("--adr-dir", default=None, help="Override ADR directory")
    parser.add_argument(
        "--level",
        choices=["basic", "standard", "strict"],
        default="basic",
        help="Normalization level",
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes (otherwise dry-run)")
    parser.add_argument("--report", action="store_true", help="Write normalization report & index")
    parser.add_argument("--report-dir", default="/config/hestia/reports", help="Reports directory")
    args = parser.parse_args()

    cfg = {}
    config_path = Path(args.config)
    if config_path.exists():
        try:
            cfg = load_toml(config_path)
        except Exception as e:
            print(f"WARN: failed to parse {config_path}: {e}")

    # Pull status aliases and other hints
    fields = cfg.get("fields", {})
    status_cfg = fields.get("status", {}) if isinstance(fields, dict) else {}
    status_aliases = (
        status_cfg.get("deprecated_aliases", {}) if isinstance(status_cfg, dict) else {}
    )

    # Determine ADR dir
    files_cfg = cfg.get("files", {}) if isinstance(cfg, dict) else {}
    adr_dir = Path(args.adr_dir or files_cfg.get("adr_directory", str(DEFAULT_ADR_DIR)))
    if not adr_dir.exists():
        print(f"ERROR: ADR directory not found: {adr_dir}")
        return 2

    md_files = [
        p for p in adr_dir.rglob("ADR-*.md")
        if "/deprecated/" not in str(p) and "/archive/" not in str(p)
    ]
    if not md_files:
        print("No ADR files found; nothing to normalize.")
        return 0

    ts = datetime.now(UTC)
    changes: list[dict] = []
    total_changed = 0

    for p in sorted(md_files):
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm, raw = extract_front_matter(text)
        if fm is None:
            # nothing to normalize
            continue
        if fm == {}:
            # parse error: do not attempt rewrites beyond TOKEN_BLOCK
            new_text, token_added = ensure_token_block(text)
            if token_added and args.apply:
                atomic_write(p, new_text)
                total_changed += 1
                changes.append(
                    {
                        "path": str(p),
                        "actions": ["token_block_added"],
                        "note": "front-matter parse failed; only token block appended",
                    }
                )
            elif token_added:
                changes.append({"path": str(p), "actions": ["token_block_added (dry-run)"]})
            continue

        original_fm = dict(fm)
        actions: list[str] = []

        # Normalize status aliases
        status = fm.get("status")
        if isinstance(status, str) and status in status_aliases:
            fm["status"] = status_aliases[status]
            actions.append(f"status_alias:{status}->{status_aliases[status]}")

        # Normalize related/supersedes to pure ADR-#### arrays
        for field in ("related", "supersedes"):
            norm = normalize_related(fm.get(field))
            if norm != fm.get(field):
                fm[field] = norm
                actions.append(f"{field}_normalized")

        # Slug regeneration (standard/strict)
        slug = fm.get("slug")
        title = fm.get("title")
        _id = fm.get("id")
        if args.level in ("standard", "strict") and isinstance(title, str):
            title_clean = title
            if isinstance(_id, str) and title_clean.startswith(_id):
                # drop ADR-XXXX prefix
                title_clean = title_clean[len(_id) :].lstrip(": ").lstrip()
            new_slug = kebab(title_clean)
            if not isinstance(slug, str) or not SLUG_RE.match(slug) or slug != new_slug:
                fm["slug"] = new_slug
                actions.append("slug_regenerated")

        # Title include ID prefix (strict)
        if (
            args.level == "strict"
            and isinstance(title, str)
            and isinstance(_id, str)
            and _id not in title
        ):
            fm["title"] = f"{_id}: {title}"
            actions.append("title_prefixed_with_id")

        # Ensure TOKEN_BLOCK exists (basic+)
        new_text, token_added = ensure_token_block(text)

        # If FM changed, rebuild the file text
        # Compare with string-coercion to handle YAML date objects safely
        fm_changed = json.dumps(original_fm, sort_keys=True, default=str) != json.dumps(
            fm, sort_keys=True, default=str
        )
        if fm_changed or token_added:
            # Reconstruct document with updated front-matter
            # Extract fm block boundaries
            m = FM_RE.search(text)
            assert m is not None
            start, end = m.span()
            fm_json = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip()
            rebuilt = f"---\n{fm_json}\n---\n" + text[end:]
            if token_added and "TOKEN_BLOCK" not in rebuilt:
                rebuilt = new_text  # fallback
            if args.apply:
                atomic_write(p, rebuilt)
                total_changed += 1
                actions = actions or ["token_block_added"] if token_added else actions
                changes.append({"path": str(p), "actions": actions})
            else:
                act = actions.copy()
                if token_added:
                    act.append("token_block_added (dry-run)")
                changes.append({"path": str(p), "actions": act or ["no-op (dry-run)"]})

    # Reporting
    if args.report:
        day_dir = Path(args.report_dir) / ts.strftime("%Y%m%d")
        day_dir.mkdir(parents=True, exist_ok=True)
        tool = "adr-frontmatter-normalize"
        report_name = f"{tool}__{ts.strftime('%Y%m%dT%H%M%SZ')}__report.log"
        report_path = day_dir / report_name
        meta = {
            "tool": tool,
            "created_at": ts.isoformat(),
            "repo_root": str(REPO_ROOT),
            "adr_dir": str(adr_dir),
            "counts": {"changed": total_changed, "files": len(md_files)},
            "level": args.level,
            "apply": bool(args.apply),
        }
        payload = {"changes": changes}
        with report_path.open("w", encoding="utf-8") as fh:
            fh.write("---\n")
            fh.write(json.dumps(meta, indent=2))
            fh.write("\n---\n")
            fh.write(json.dumps(payload, indent=2))
            fh.write("\n")
        # Stable latest
        try:
            base_dir = Path(args.report_dir)
            base_dir.mkdir(parents=True, exist_ok=True)
            latest_path = base_dir / "adr-frontmatter-normalize.latest.log"
            tmp = base_dir / (latest_path.name + ".tmp")
            with tmp.open("w", encoding="utf-8") as fh:
                fh.write("---\n")
                fh.write(json.dumps(meta, indent=2))
                fh.write("\n---\n")
                fh.write(json.dumps(payload, indent=2))
                fh.write("\n")
            os.replace(tmp, latest_path)
        except Exception as e:
            print(f"WARN: failed writing latest normalization report: {e}")
        # Index JSONL
        try:
            index_path = Path(args.report_dir) / "_index.jsonl"
            with index_path.open("a", encoding="utf-8") as idx:
                idx.write(json.dumps({
                    "created_at": ts.isoformat(),
                    "tool": tool,
                    "path": str(report_path),
                    "counts": meta["counts"],
                    "level": args.level,
                    "apply": bool(args.apply),
                }) + "\n")
        except Exception:
            pass
        print(f"Report written: {report_path}")

    status = "applied" if args.apply else "completed (dry-run)"
    print(f"Normalization {status}; files changed: {total_changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
