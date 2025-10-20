#!/usr/bin/env python3
"""
Validator: validator_registry_entities.py
Scans a YAML file for Home Assistant entity ids, compares them against
.core.entity_registry and emits a detailed JSON/YAML report with fuzzy-match
suggestions for unmatched entities.

Location: hestia/tools/utils/validators/validator_registry_entities.py
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except Exception:
    print("Missing dependency: pyyaml is required. Install with: pip install pyyaml")
    raise

# Regex patterns for entity detection
ENTITY_PATTERNS = {
    'binary_sensor': r'\bbinary_sensor\.[a-zA-Z0-9_]+\b',
    'sensor': r'\bsensor\.[a-zA-Z0-9_]+\b',
    'light': r'\blight\.[a-zA-Z0-9_]+\b',
    'switch': r'\bswitch\.[a-zA-Z0-9_]+\b',
    'input_boolean': r'\binput_boolean\.[a-zA-Z0-9_]+\b',
    'var': r'\bvar\.[a-zA-Z0-9_]+\b',
    'automation': r'\bautomation\.[a-zA-Z0-9_]+\b',
    'group': r'\bgroup\.[a-zA-Z0-9_]+\b'
}

DEFAULTS = {
    # Leave registry/output/temp to be computed at runtime from .env/HA_MOUNT/HESTIA_WORKSPACE
    'FUZZY_MATCH_THRESHOLD': 0.7,
}

# dataclasses for structured output
@dataclass
class EntityMatch:
    entity_id: str
    domain: str
    found_in_registry: bool
    exact_match: bool
    fuzzy_matches: List[Tuple[str, float]]
    context_line: Optional[str] = None


@dataclass
class ValidationReport:
    input_file: str
    timestamp: str
    total_entities: int
    exact_matches: int
    fuzzy_matches: int
    unmatched: int
    success_rate: float
    entities: List[EntityMatch]
    registry_stats: Dict[str, int]


def load_env_overrides() -> Dict[str, str]:
    # Simple .env loader (file optional)
    env_path = Path('.env')
    out = {}
    if env_path.exists():
        for ln in env_path.read_text(encoding='utf8').splitlines():
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            if '=' not in ln:
                continue
            k, v = ln.split('=', 1)
            k = k.strip()
            # support lines that start with 'export VAR=..'
            if k.startswith('export '):
                k = k[len('export '):]
            out[k] = v.strip().strip('"').strip("'")
    return out


def compile_entity_regexes():
    return {k: re.compile(v) for k, v in ENTITY_PATTERNS.items()}


def extract_entities_from_text(text: str) -> List[Tuple[str, str, str]]:
    """Return list of tuples (entity_id, domain, context_line)"""
    regexes = compile_entity_regexes()
    results: List[Tuple[str, str, str]] = []
    for i, line in enumerate(text.splitlines()):
        for domain, rx in regexes.items():
            for m in rx.finditer(line):
                results.append((m.group(0), domain, line.strip()))
    # dedupe preserving order
    seen = set()
    deduped = []
    for e in results:
        if e[0] not in seen:
            seen.add(e[0])
            deduped.append(e)
    return deduped


def load_registry(path: Path) -> Dict[str, dict]:
    if not path.exists():
        raise FileNotFoundError(f"Entity registry not found at {path}")
    raw = path.read_text(encoding='utf8')
    try:
        # entity registry is JSON-like
        import json as _json
        data = _json.loads(raw)
    except Exception as exc:
        raise RuntimeError(f"Failed to parse registry JSON: {exc}")
    # expect top-level data.entities -> list
    entities = data.get('data', {}).get('entities') or data.get('entities')
    if entities is None:
        raise RuntimeError('Unexpected registry shape; missing entities list')
    out = {}
    for ent in entities:
        entity_id = ent.get('entity_id')
        if entity_id:
            out[entity_id] = ent
    return out


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def fuzzy_suggest(entity: str, registry_keys: List[str], threshold: float) -> List[Tuple[str, float]]:
    scored = [(k, similarity(entity, k)) for k in registry_keys]
    scored = [s for s in scored if s[1] >= threshold]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:10]


def ensure_dirs(out_dir: Path, tmp_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)


def write_report(report: ValidationReport, out_file: Path, fmt: str = 'json'):
    if fmt == 'json':
        with out_file.open('w', encoding='utf8') as fh:
            json.dump(asdict(report), fh, indent=2, ensure_ascii=False)
    else:
        with out_file.open('w', encoding='utf8') as fh:
            yaml.safe_dump(asdict(report), fh, sort_keys=False)


def parse_args():
    p = argparse.ArgumentParser(description='Validate Home Assistant YAML entities against core.entity_registry')
    p.add_argument('-i', '--input', help='Input YAML file path (relative or absolute)')
    p.add_argument('-o', '--output', help='Output report path (optional)')
    p.add_argument('--registry-path', help='Path to core.entity_registry JSON')
    p.add_argument('--fuzzy-threshold', type=float, help='Fuzzy similarity threshold (0-1)')
    p.add_argument('--format', choices=['json', 'yaml'], default='json', help='Report format')
    p.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    return p.parse_args()


def main():
    args = parse_args()

    env = {**DEFAULTS, **load_env_overrides()}
    # compute HA root and hestia workspace from centralized .env variables
    ha_mount = Path(os.environ.get('HA_MOUNT') or env.get('HA_MOUNT') or os.path.expanduser('~/hass'))
    hestia_workspace = Path(os.environ.get('HESTIA_WORKSPACE') or env.get('HESTIA_WORKSPACE') or str(ha_mount / 'hestia' / 'workspace'))

    default_registry = ha_mount / '.storage' / 'core.entity_registry'
    default_out_dir = hestia_workspace / 'operations' / 'reports' / 'validator_registry_entities'
    default_tmp_dir = ha_mount / 'tmp' / 'validator_registry_entities'

    registry_path = Path(args.registry_path) if args.registry_path else default_registry
    out_dir = Path(args.output) if args.output else default_out_dir
    tmp_dir = Path(env.get('VALIDATOR_TEMP_DIR') or default_tmp_dir)
    fuzzy_threshold = float(args.fuzzy_threshold) if args.fuzzy_threshold is not None else float(env.get('FUZZY_MATCH_THRESHOLD', DEFAULTS['FUZZY_MATCH_THRESHOLD']))

    ensure_dirs(out_dir, tmp_dir)

    # interactive input if not provided
    input_path: Optional[Path] = Path(args.input) if args.input else None
    if input_path is None:
        try:
            answer = input('Enter path to YAML file to validate (relative to repo root): ').strip()
        except KeyboardInterrupt:
            print('\nCancelled')
            sys.exit(1)
        if not answer:
            print('No input provided. Exiting.')
            sys.exit(1)
        input_path = Path(answer)

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        sys.exit(2)

    text = input_path.read_text(encoding='utf8')
    entities = extract_entities_from_text(text)
    registry = load_registry(registry_path)
    registry_keys = list(registry.keys())

    entity_matches: List[EntityMatch] = []
    exact = 0
    fuzzy_cnt = 0
    unmatched = 0

    for ent_id, domain, ctx in entities:
        found = ent_id in registry
        fuzzy = []
        if found:
            exact += 1
            em = EntityMatch(ent_id, domain, True, True, [], ctx)
        else:
            suggestions = fuzzy_suggest(ent_id, registry_keys, fuzzy_threshold)
            if suggestions:
                fuzzy_cnt += 1
                fuzzy = suggestions
                em = EntityMatch(ent_id, domain, False, False, fuzzy, ctx)
            else:
                unmatched += 1
                em = EntityMatch(ent_id, domain, False, False, [], ctx)
        entity_matches.append(em)

    total = len(entity_matches)
    success_rate = round(((exact + fuzzy_cnt) / total * 100) if total else 100.0, 2)

    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    out_file = out_dir / f"{ts}_validate_{input_path.name}.{args.format}"
    tmp_file = tmp_dir / f"{ts}_validate_{input_path.name}.json"

    registry_stats = { 'total_registry_entities': len(registry_keys) }
    report = ValidationReport(
        input_file=str(input_path),
        timestamp=ts,
        total_entities=total,
        exact_matches=exact,
        fuzzy_matches=fuzzy_cnt,
        unmatched=unmatched,
        success_rate=success_rate,
        entities=entity_matches,
        registry_stats=registry_stats,
    )

    write_report(report, out_file, fmt=args.format)
    write_report(report, tmp_file, fmt='json')

    # echo summary
    print('\n📊 Entity Validation Summary')
    print(f"Input File: {input_path}")
    print(f"Entities Found: {total}")
    print(f"Exact Matches: {exact}")
    print(f"Fuzzy Matches: {fuzzy_cnt}")
    print(f"Unmatched: {unmatched}")
    print(f"Success Rate: {success_rate}%")
    print(f"Report: {out_file}")
    print('\nTop unmatched / fuzzy examples:')
    for em in entity_matches[:20]:
        if not em.exact_match:
            print(f" - {em.entity_id} (domain: {em.domain}) suggestions: {em.fuzzy_matches}")


if __name__ == '__main__':
    main()
