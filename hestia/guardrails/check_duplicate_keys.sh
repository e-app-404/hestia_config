#!/usr/bin/env bash
# Detect duplicate YAML keys across repo (fails on any dup).
import sys, os, glob
from ruamel.yaml import YAML
from ruamel.yaml.constructor import DuplicateKeyError
yaml = YAML(typ='rt')
yaml.allow_duplicate_keys = False
ROOT = "."
paths = [p for p in glob.glob(f"{ROOT}/**/*.yaml", recursive=True)]
errors = 0
for p in paths:
    try:
        with open(p, "r", encoding="utf-8") as f:
            yaml.load(f)
    except DuplicateKeyError as e:
        print(f"[DUPKEY] {p}: {e}", file=sys.stderr)
        errors += 1
    except Exception:
        # non-fatal parse error handled by validate_config.sh
        pass
if errors:
    sys.exit(1)
