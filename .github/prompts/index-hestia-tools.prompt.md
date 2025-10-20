---
description: 'Create a governance-aware index of all *.sh and *.py in /config/hestia/tools with purpose, scope, environment, usage, and ADR compliance insights.'
mode: 'agent'
tools: ['edit', 'search', 'runCommands', 'problems', 'changes', 'ms-python.python/getPythonEnvironmentInfo', 'ms-python.python/getPythonExecutableCommand', 'ms-python.python/installPythonPackage', 'ms-python.python/configurePythonEnvironment']
---

# Index Hestia Tools Catalog (governance-aware)

## Mission

Build a detailed, governance-aware index of every shell and Python script under `/config/hestia/tools`, identifying purpose, scope, target environment(s), usage/entry points, and ADR compliance risks. Produce actionable insights and a safe refactor plan without changing any files.

## Scope & Preconditions

- Analyze only scripts in `/config/hestia/tools/**` with extensions `.sh` and `.py`.
- Do NOT modify or move files; analysis-only. Respect ADR-0024 and ADR-0027.
- Prioritize correctness and token efficiency. Sample content (top 120-200 LOC) unless deeper read is required.
- Call out critical runtime links: anything referenced by HA configs (automations, shell_command, scripts, tasks.json, bin/* wrappers, add-on configs) must be flagged.

## Inputs

- Base path: `/config/hestia/tools`
- Exceptions (likely good/new): `sweeper/**`, `lineage_guardian/**`
- Governance references:
  - ADR-0024 Canonical config mount `/config`
  - ADR-0027 Write-broker & atomic writes
  - ADR-0018 Workspace lifecycle & sweeper
  - ADR-0008 Normalization & determinism

## Workflow

1) Discovery
- Use file search to list all `**/*.sh` and `**/*.py` under base path.
- Build initial table with: path, type, and parent module.

2) Lightweight content sampling
- For each file, read the first ~120 lines (or full if smaller) to extract:
  - Shebang and interpreter (bash/zsh/sh/python3)
  - Title/description from header comments or docstring
  - Notable imports/includes (e.g., `require-config-root.sh`, `toml`, `yaml`)
  - Path usage patterns (`/config`, `/tmp`, `/Volumes/…`, `write-broker` calls)
  - Guardrails (dry-run flags, backups, atomic writes)

3) Cross-references and usage mapping
- Grep the workspace for references to each script path. Classify usage:
  - Invoked by HA (shell_command/rest_command/templates), by `bin/*` wrappers, or by VS Code tasks.
  - Internal-only helpers vs user-facing CLIs.

4) Governance checks (heuristic)
- ADR-0024: Flag non-canonical paths (e.g., `/Volumes/...`, `~/hass`, `/tmp` instead of `tmp/`).
- ADR-0027: Note use (or absence) of write-broker and atomic file ops.
- ADR-0018: If touching workspace lifecycle artifacts, flag sweeper compliance.

5) Classification
- Category: diagnostics, maintenance, cleanup, install/bootstrap, pipelines, appdaemon, adr, prompt, etc.
- Stability: stable, candidate for refactor, deprecated, legacy.
- Risk: low/medium/high based on entry-point usage and side-effects.

6) Outputs
- JSON index (structured, sorted keys) with one object per file:
  - path, name, type, interpreter, title, description, category, usage, invoked_by, risk, governance_flags[], adr_notes[], notes
- Markdown report with summary counts, hot alerts, and recommended refactor batches.
- Do not write files unless explicitly authorized; return results in Chat.

## Output Expectations

- A concise executive summary followed by:
  - Alerts: scripts used by HA runtime or critical tasks.
  - JSON index (pretty-printed) for downstream tooling.
  - Suggested refactor/merge/deprecate plan in small, safe batches.

## Quality Assurance

- Validate sampling vs full-file needs: if header lacks description, peek deeper for clear purpose.
- If a script appears unused, confirm with repo-wide grep (case-insensitive) before marking.
- Include caveats where inference is uncertain.

## Guardrails

- No file changes. No secrets. Respect canonical path contracts and write-broker policy in recommendations.
- Provide explicit ADR citations for any compliance findings.

## Handoff Notes (token-aware)

- Prefer short file excerpts over full dumps; summarize intent.
- Consolidate repeated findings (e.g., same pattern across many scripts) once in the report.
