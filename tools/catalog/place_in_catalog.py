#!/usr/bin/env python3
"""Compatibility shim delegating to canonical hestia/tools implementation.

Canonical: /config/hestia/tools/catalog/place_in_catalog.py
This file exists to keep older references working while enforcing ADR-0024.
"""
import os
import runpy
import sys

CONFIG_ROOT = os.environ.get("CONFIG_ROOT", "/config")
TARGET = os.path.join(CONFIG_ROOT, "hestia/tools/catalog/place_in_catalog.py")

if not os.path.exists(TARGET):
    sys.stderr.write(f"ERROR: canonical script not found at {TARGET}\n")
    sys.exit(127)

sys.argv[0] = TARGET
runpy.run_path(TARGET, run_name="__main__")
