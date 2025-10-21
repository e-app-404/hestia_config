#!/usr/bin/env python3
import sys
import re
from pathlib import Path

UID_RE = re.compile(r"^\s*unique_id:\s*['\"]?([^'\"\s]+)['\"]?\s*$")

def main() -> int:
    seen = {}
    dup = False
    files = [Path(x) for x in _git_ls_files('*.yaml')]
    for p in files:
        try:
            for i, line in enumerate(p.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
                m = UID_RE.match(line)
                if m:
                    uid = m.group(1)
                    if uid in seen:
                        print(f"Duplicate unique_id '{uid}': {seen[uid]} and {p}:{i}")
                        dup = True
                    else:
                        seen[uid] = f"{p}:{i}"
        except Exception:
            continue
    if dup:
        return 1
    print("OK: unique_id values unique.")
    return 0

def _git_ls_files(pattern: str):
    import subprocess
    return subprocess.check_output(['git', 'ls-files', pattern]).decode().splitlines()

if __name__ == '__main__':
    sys.exit(main())
