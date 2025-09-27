"""Reporting utilities for linter results."""
from typing import List, Dict, Any
import json


def format(results: List[Dict[str, Any]]) -> str:
    out = []
    for r in results:
        out.append(f"== {r['file']} ==")
        if not r['violations']:
            out.append("  OK")
        else:
            for v in r['violations']:
                out.append(f"  - [{v['severity'].upper()}] {v['rule']}:{v['line']} ({v.get('lang','')}) {v['message']}")
    return "\n".join(out)


def to_json(results: List[Dict[str, Any]]) -> str:
    return json.dumps(results, indent=2)
