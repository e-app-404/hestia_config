#!/usr/bin/env python3
import pathlib
import sys

root = pathlib.Path("hestia/reports")
if not root.exists():
    print("NOREPORTS")
    sys.exit(0)

candidates=[]
for day in sorted(root.glob("[0-9]"*8)):
    for batch in day.glob("*__*"):
        if batch.is_dir(): candidates.append(batch)
if not candidates:
    print("NO_BATCHES")
    sys.exit(0)

latest = max(candidates, key=lambda p: p.stat().st_mtime)
link = root / "latest"
try:
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(latest.relative_to(root))
    print(f"LATEST -> {latest}")
except OSError:
    # FS without symlinks: write a text pointer instead
    with open(root / "latest.path", "w") as f:
        f.write(str(latest)+"\n")
    print(f"LATEST_FILE -> {latest}")