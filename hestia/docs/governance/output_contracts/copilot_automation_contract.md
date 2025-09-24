# Copilot Automation Contract

## Prelude for Every Task

Always begin with: `source ~/ha_path.sh || echo "BLOCKED: locator" && exit 2`
Use `$HESTIA_CONFIG` and `${HESTIA_CONFIG_FILE}` for all paths.
On every action, emit:
  OK: <what succeeded>
  BLOCKED: <why>
  EVIDENCE: <path|json>
On failure, propose a one-liner fix.

## Examples

```bash
source ~/ha_path.sh || exit 2
git -C "$HESTIA_CONFIG" rev-parse --show-toplevel || echo "EVIDENCE: not a git work tree"
[ -f "$HESTIA_CONFIG/configuration.yaml" ] || echo "BLOCKED: missing configuration.yaml at $HESTIA_CONFIG"
```

## Guardrails & Output Contracts

- All automations/scripts must:
  - Use `$HESTIA_CONFIG` for all repo paths.
  - Never mutate system files without explicit user confirmation.
  - Emit status tokens for success, failure, and evidence.
  - Propose corrective actions on failure.
