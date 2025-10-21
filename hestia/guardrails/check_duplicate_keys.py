#!/usr/bin/env python3
import sys
from pathlib import Path

try:
    from ruamel.yaml import YAML
    from ruamel.yaml.constructor import DuplicateKeyError
except Exception:  # pragma: no cover
    YAML = None
    DuplicateKeyError = Exception

def scan_file(p: Path) -> bool:
    if YAML is None:
        # Fallback: naive duplicate key detector using simple parse of lines
        # Not fully accurate but better than nothing when ruamel isn't present.
        keys = {}
        ok = True
        for i, line in enumerate(p.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
            if line.lstrip().startswith('#'):
                continue
            if ':' in line and not line.startswith('  - '):
                k = line.split(':', 1)[0].strip()
                if k:
                    if (k, line.count(' ')) in keys:
                        print(f"Duplicate-like key '{k}' at {p}:{i}")
                        ok = False
                    keys[(k, line.count(' '))] = i
        return ok
    yaml = YAML(typ='rt')
    try:
        with p.open('r', encoding='utf-8') as fh:
            yaml.load(fh)
        return True
    except DuplicateKeyError as e:
        print(f"Duplicate key in {p}: {e}")
        return False
    except Exception:
        # Ignore other YAML errors here; other checks will catch syntax.
        return True

def main() -> int:
    files = [Path(f) for f in sys.stdin.read().splitlines() if f.endswith('.yaml')]
    if not files:
        # default to git tracked yaml
        import subprocess
        out = subprocess.check_output(['git', 'ls-files', '*.yaml']).decode().splitlines()
        files = [Path(x) for x in out]
    ok = True
    for p in files:
        if not scan_file(p):
            ok = False
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
