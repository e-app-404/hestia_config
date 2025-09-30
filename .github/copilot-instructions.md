<!-- Copilot instructions for Hestia (Home Assistant workspace) -->
# Quick guide for AI coding assistants

This repository (Hestia) is a collection of operator tooling, config artifacts
and small utilities that live alongside a Home Assistant installation. Use the
notes below to be productive quickly and avoid unsafe changes.

- Big picture: look under `hestia/` for the main components:
  - `hestia/config/` — runtime configurations, device configs, and network topology.
  - `hestia/tools/` — CLI helpers and small utilities (e.g. ADR linter at
    `hestia/tools/utils/validators/adr_lint`).
  - `hestia/workspace/archive/vault/` & `hestia/tools/utils/vault_manager/` — secret templates and
    import helpers; repository stores placeholders only (never real secrets).

- Workflows and commands:
  - Python CLIs published in `pyproject.toml` (see `hestia-adr-lint` entry).
    To run ADR linter locally follow `README.md`: create a venv under ~ (not
    under the HA mount) and run `hestia-adr-lint hestia/library/docs/ADR --format human`.
  - Many deploy/scripts are dry-run by default. Check `--help` or README for
    `--apply` or `--execute` flags before making changes (examples: `deploy/dsm` scripts).

- Project conventions you must preserve:
  - Never commit real credentials. Vault templates use `__REPLACE_ME__` placeholders.
  - Preview vs provisioning separation: files under `hestia/config` are
    machine-friendly previews; actual credential injection/provisioning happens
    outside this repo. Don’t hardcode secrets into renderers or templates.
  - Tooling assumes Python >= 3.10 and ruff settings in `pyproject.toml` (line-length 100).

- Integration points to watch for:
  - `vault://` URIs in YAML (e.g. `hestia/config/storage/samba.yaml`) map to
    vault paths like secret/hestia/.... Code expects the fragment convention such as #credentials.
  - Tailscale / network artifacts live under `hestia/config/network` and are used by
    preview and deployment scripts.

- Files to read when making edits:
  - `pyproject.toml` — packaging and entrypoints
  - `README.md` at repo root — quick dev/run instructions
  - `hestia/tools/*` — small CLIs; run unit-level CLI manually in a venv
  - `hestia/workspace/archive/vault/templates/` and `hestia/tools/utils/vault_manager/README.md` — secret naming

- Examples of project patterns:
  - ADR linter: `hestia/tools/utils/validators/adr_lint` — CLI entry `hestia.tools.adr_lint.cli:main`.
  - Dry-run deploy script: `hestia/deploy/dsm/apply_portal_changes.sh` uses `--apply` to perform changes.

- Safety notes for AI agents:
  - Prefer edits that add tests, docs, or non-destructive refactors.
  - Flag any change that would introduce plaintext secrets or modify system services
    (rely on maintainers to run deployment steps).

If anything here is unclear or you need more detail on a subcomponent, say which
area (e.g. `vault templates`, `adr linter`, `deploy/dsm`) and I will expand the
instructions with file-level examples.

