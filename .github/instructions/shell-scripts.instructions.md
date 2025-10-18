---
description: 'Conventions for shell scripts in scripts/** and hestia/tools/**'
applyTo: 'scripts/**/*.sh, hestia/tools/**/*.sh'
---

## Shell Scripts (Ops/Tooling)

### General Instructions
- Start scripts with: `set -Eeuo pipefail` and `IFS=$'\n\t'`.
- Use canonical config path `/config` (ADR-0024). Avoid `/tmp`; use repo `tmp/` per ADR-0018.
- Prefer read-only operations by default; require explicit flags for writes.

### Best Practices
- Use functions; keep main flow at bottom.
- Log key steps; exit with clear messages.
- For any writes to repo files, use write-broker (ADR-0027).

### Code Standards
- Use Bash when Bash features are needed: `#!/usr/bin/env bash`.
- Quote variables; avoid word splitting; use arrays.
- For HA commands, use `bash -lc '/config/path'` pattern (see governance guide).

### Common Patterns
- Dry-run (`--dry-run`) default; `--apply` to perform changes.
- Atomic operations via write-broker with safe replace patterns.

### Security
- Never echo secrets; redact logs.
- Validate inputs; sanitize untrusted values.

### Performance
- Avoid subshells in tight loops; prefer built-ins.
- Use `set -o pipefail` to catch pipeline failures.

### Testing (quick checks)
- Task: ADR-0024: Lint Paths
- Optional: `bash -n script.sh` for syntax check
- Validate effects with HA config-validate tasks when scripts modify YAML.

### Examples
Good

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_ROOT="/config"
: "${CONFIG_ROOT:?Missing CONFIG_ROOT}"

main() {
  echo "Path health check..."
  "${CONFIG_ROOT}/bin/config-health" "${CONFIG_ROOT}"
}
main "$@"

Bad
#!/bin/sh
rm -rf /config/* # unsafe, no guards
echo done

### References
- /config/hestia/library/docs/ADR/ADR-0024-canonical-config-path.md
- /config/hestia/library/docs/ADR/ADR-0027-file-writing-governance.md
- /config/hestia/library/docs/ADR/ADR-0018-workspace-lifecycle-policy.md
- /config/.github/instructions/copilot-instructions.md
