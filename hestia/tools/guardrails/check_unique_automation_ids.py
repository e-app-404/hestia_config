#!/usr/bin/env python3
import re
import sys
from pathlib import Path

ID_RE = re.compile(r"^\s*id:\s*([A-Za-z0-9_\-]+)\s*$")

def main() -> int:
    out = {}
    dup = False
    files = [Path(x) for x in _git_ls_files('*.yaml')]
    for p in files:
        try:
            for i, line in enumerate(
                p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
            ):
                m = ID_RE.match(line)
                if m:
                    k = m.group(1)
                    if k in out:
                        print(f"Duplicate automation id '{k}': {out[k]} and {p}:{i}")
                        dup = True
                    else:
                        out[k] = f"{p}:{i}"
        except Exception:
            continue
    if dup:
        return 1
    print("OK: automation ids unique.")
    return 0

def _git_ls_files(pattern: str):
    import subprocess
    return subprocess.check_output(['git', 'ls-files', pattern]).decode().splitlines()

if __name__ == '__main__':
    sys.exit(main())
