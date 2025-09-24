#!/usr/bin/env python3
# Purpose: Generate secrets.example.yaml by redacting values from secrets.yaml
# Safety:   - Never prints real secret values
#           - Writes to repo root as 'secrets.example.yaml'
# Usage:    python3 hestia/ops/scripts/gen_secrets_example.py

import re
import sys
from pathlib import Path

try:
    import yaml  # PyYAML
except Exception:
    yaml = None
    # We'll fall back to a conservative line-based redaction if PyYAML isn't available.

REDACTED = "REDACTED"

def redact(obj):
    if isinstance(obj, dict):
        return {k: redact(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(v) for v in obj]
    # Scalars -> replace with placeholder
    return REDACTED


def redacted_from_text(text: str) -> str:
    """Conservative fallback redaction that doesn't parse full YAML.

    - Replaces inline scalar values after a ':' with the REDACTED token.
    - Collapses block scalars (|, >) into a single REDACTED value.
    - Replaces list items with '- REDACTED'.
    - Preserves comments and blank lines where reasonably possible.

    This intentionally avoids printing or returning any real secret values.
    """
    lines = text.splitlines()
    out_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()

        # Preserve comments and empty lines
        if stripped.startswith('#') or stripped == '':
            out_lines.append(line)
            i += 1
            continue

        # Key: value on single line
        m = re.match(r'^(\s*)([^:\s][^:]*?):\s*(.*)$', line)
        if m:
            indent, key, val = m.groups()
            # Block scalar start: collapse entire block into a single REDACTED
            if val in ('|', '>'):
                out_lines.append(f"{indent}{key}: {REDACTED}")
                j = i + 1
                # skip subsequent indented block lines
                while j < len(lines):
                    nl = lines[j]
                    if nl.strip() == '':
                        j += 1
                        continue
                    if len(nl) - len(nl.lstrip()) > len(indent):
                        j += 1
                        continue
                    break
                i = j
                continue

            # Inline comment handling: try to preserve trailing comment starting with '#'
            comment_pos = val.find(' #')
            if comment_pos != -1:
                comment = val[comment_pos + 1:]
                out_lines.append(f"{indent}{key}: {REDACTED}{comment}")
            else:
                out_lines.append(f"{indent}{key}: {REDACTED}")
            i += 1
            continue

        # List item: replace item value
        if stripped.startswith('- '):
            indent = line[: len(line) - len(line.lstrip())]
            out_lines.append(f"{indent}- {REDACTED}")
            i += 1
            continue

        # Fallback: preserve the line as-is
        out_lines.append(line)
        i += 1

    return '\n'.join(out_lines) + '\n'

def main():
    repo_root = Path(__file__).resolve().parents[3]  # /n/ha
    src = repo_root / "secrets.yaml"
    dst = repo_root / "secrets.example.yaml"

    if not src.exists():
        sys.stderr.write(f"ERROR: {src} not found. Run from a workspace that contains secrets.yaml\n")
        sys.exit(2)

    text = src.read_text()

    if yaml is not None:
        data = yaml.safe_load(text) or {}
        red = redact(data)

        # Write with stable formatting, no aliases
        class NoAliasDumper(yaml.SafeDumper):
            def ignore_aliases(self, data):
                return True

        out = yaml.dump(red, Dumper=NoAliasDumper, sort_keys=True, default_flow_style=False)
    else:
        # PyYAML not available — use a safe, conservative textual redaction.
        sys.stderr.write("WARNING: PyYAML not available, using conservative fallback redaction.\n")
        out = redacted_from_text(text)

    dst.write_text(out)
    print(f"Wrote {dst}")

if __name__ == "__main__":
    main()
