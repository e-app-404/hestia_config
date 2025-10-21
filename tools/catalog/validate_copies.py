#!/usr/bin/env python3
"""Compatibility shim that delegates to canonical tool under hestia/tools.

Per ADR-0024, the canonical implementation lives at
  /config/hestia/tools/catalog/validate_copies.py
This wrapper preserves older references to /config/tools/… paths.
"""
import os
import runpy
import sys

CONFIG_ROOT = os.environ.get("CONFIG_ROOT", "/config")
TARGET = os.path.join(CONFIG_ROOT, "hestia/tools/catalog/validate_copies.py")

if not os.path.exists(TARGET):
    sys.stderr.write(f"ERROR: canonical script not found at {TARGET}\n")
    sys.exit(127)

# Ensure argv[0] reflects the target for better error messages
sys.argv[0] = TARGET
runpy.run_path(TARGET, run_name="__main__")
