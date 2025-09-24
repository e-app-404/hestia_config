"""Formatting and JSON reporting for linter results."""
import json
from typing import Any, Dict, List


def format(results: List[Dict[str, Any]]) -> str:
    out = []
    for r in results:
        out.append(f"== {r['file']} ==")
        if not r['violations']:
            out.append("  OK")
        else:
            for v in r['violations']:
                out.append(f"  - {v}")
    return "\n".join(out)


def to_json(results: List[Dict[str, Any]]) -> str:
    return json.dumps(results, indent=2)
