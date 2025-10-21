#!/usr/bin/env python3

"""
Validate area_mapping.yaml against three system requirements:
- Motion Lighting: all entries with motion_lighting capability must be areas or subareas
- Vacuum Control: entries with vacuum_control must have segment_id (int)
- Activity Tracker: no service/outside/system nodes permitted

Usage:
  python3 /config/hestia/tools/diag/validate_area_mapping.py
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

MAPPING = Path("/config/www/area_mapping.yaml")


def main() -> int:
    data = yaml.safe_load(MAPPING.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    errors: list[str] = []

    valid_types = {"area", "subarea"}
    for n in nodes:
        nid = n.get("id")
        ntype = n.get("type")
        caps = (n.get("capabilities") or {})
        # activity tracker: forbid non-physical types
        if ntype not in valid_types:
            errors.append(f"node {nid}: invalid type {ntype} (must be area or subarea)")
        # motion lighting: any presence of motion_lighting is valid on area/subarea
        if "motion_lighting" in caps and ntype not in valid_types:
            errors.append(f"node {nid}: motion_lighting only allowed for areas/subareas")
        # vacuum control: require integer segment_id
        if "vacuum_control" in caps:
            vc = caps["vacuum_control"] or {}
            if not isinstance(vc.get("segment_id"), int):
                errors.append(f"node {nid}: vacuum_control.segment_id must be integer")

    out = {"file": str(MAPPING), "errors": errors, "valid": not errors}
    print(json.dumps(out, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
