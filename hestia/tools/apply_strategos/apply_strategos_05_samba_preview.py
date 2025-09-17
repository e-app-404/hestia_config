#!/usr/bin/env python3
import json
import os
import re
import sys
import tarfile
from pathlib import Path

import yaml

ENV = {}
with open(os.environ["OUT_DIR"] + "/.env.meta") as f:
    for line in f:
        if "=" in line:
            k, v = line.strip().split("=", 1)
            ENV[k] = v
OUT_DIR = Path(ENV["OUT_DIR"])
SCRATCH_TGZ = ENV.get("SCRATCH_TGZ")
SCRATCH_DIR = ENV.get("SCRATCH_DIR")
PREVIEW = OUT_DIR / "preview"
PREVIEW.mkdir(parents=True, exist_ok=True)


def load_overlay():
    name = "20250911-patch-network.conf-samba.extract"
    if SCRATCH_TGZ and SCRATCH_TGZ is not None and os.path.isfile(SCRATCH_TGZ):
        with tarfile.open(SCRATCH_TGZ, "r:gz") as t:
            m = t.getmember(f"scratch/{name}")
            extracted = t.extractfile(m)
            if extracted is None:
                raise FileNotFoundError(
                    f"Could not extract {name} from {SCRATCH_TGZ}"
                )
            return extracted.read().decode("utf-8")
    elif SCRATCH_DIR is not None:
        return Path(SCRATCH_DIR, name).read_text(encoding="utf-8")
    else:
        raise FileNotFoundError("SCRATCH_TGZ and SCRATCH_DIR are not set")


doc = yaml.safe_load(load_overlay())
global_kv = doc.get("global", {}) if isinstance(doc, dict) else {}
shares = doc.get("shares", {}) if isinstance(doc, dict) else {}

lines = []
lines.append("[global]")
for k in sorted(global_kv.keys(), key=str.lower):
    lines.append(f"{k} = {global_kv[k]}")
for name in sorted(shares.keys(), key=str.lower):
    lines.append(f"[{name}]")
    for k in sorted(shares[name].keys(), key=str.lower):
        lines.append(f"{k} = {shares[name][k]}")
content = "\n".join(lines).strip() + "\n"
# lint: ensure single [global], alpha shares, no hardening keys
content = "\n".join(lines).strip() + "\n"
# lint: ensure single [global], alpha shares, no hardening keys
lint = {
    "single_global": content.count("[global]") == 1,
    "alpha_shares": sorted(shares) == list(shares.keys()),
}
forbidden = {"server min protocol", "hosts allow", "interfaces"}
lint["no_hardening"] = all(
    re.search(rf"^{re.escape(k)}\s*=", content, flags=re.I | re.M) is None
    for k in forbidden
)

(PREVIEW / "smb.conf").write_text(content, encoding="utf-8")
(OUT_DIR / "notes" / "SAMBA_LINT.json").write_text(
    json.dumps(lint, indent=2), encoding="utf-8"
)
if not (lint["single_global"] and lint["no_hardening"]):
    print("BLOCKED: VALIDATION -> samba_preview: lint failed", file=sys.stderr)
    sys.exit(3)
print(json.dumps(lint, indent=2))
