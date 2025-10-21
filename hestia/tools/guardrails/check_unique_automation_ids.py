#!/usr/bin/env python3
"""Wrapper delegating to canonical guardrails implementation.

Canonical home: /config/hestia/guardrails/check_unique_automation_ids.py
This wrapper lives under /config/hestia/tools to provide a unified tools namespace.
"""
import os
import runpy
import sys

CONFIG_ROOT = os.environ.get("CONFIG_ROOT", "/config")
TARGET = os.path.join(CONFIG_ROOT, "hestia/guardrails/check_unique_automation_ids.py")

if not os.path.exists(TARGET):
    sys.stderr.write(f"ERROR: canonical script not found at {TARGET}\n")
    sys.exit(127)

sys.argv[0] = TARGET
runpy.run_path(TARGET, run_name="__main__")
