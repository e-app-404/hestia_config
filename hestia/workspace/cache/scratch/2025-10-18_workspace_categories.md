# categories.md

## Category Table

| Category	| Rule (glob)	| Rationale	| Typical pitfalls	| Validation hooks |
| HA Packages YAML	| packages/**/*.yaml	| HA runtime config delivered via packages	| Key order/indent drift; unsorted lists; path non-compliance	| Task: ADR-0024: Validate HA YAML & Core; Task: ADR-0024: Path Health |
| HA Domain Templates YAML	| domain/templates/**/*.yaml	| Core template logic for sensors/virtual entities	| Unguarded Jinja; using functions not filters; unknown/unavailable	| Task: Hestia: Patch HA templates; Task: ADR-0024: Validate HA YAML & Core |   
| HA Domain YAML (non-template)	| domain/{automations,binary_sensors,command_line,frontend,geo_location,groups,helpers,lights,notify,persons,scripts,sensors,weather,zones}/**/*.yaml	| Non-template domain definitions loaded by HA	| Cross-domain leakage; naming inconsistencies; IDs drift	| Task: ADR-0024: Validate HA YAML & Core |
| Custom Jinja Templates	| custom_templates/**/*.{jinja,jinja2,yaml}	| Macro libraries and templating helpers	| Whitespace noise; state normalization gaps; accidental side effects	| Task: Hestia: Patch HA templates |
| Shell Scripts	| **/*.sh, **/*.bash	| Operational tooling & pipelines	| Non-canonical paths; missing set -Eeuo pipefail; unsafe rm	| Task: ADR-0024: Lint Paths; Optional: bash -n file.sh |
| HA Blueprints YAML	| blueprints//*.yaml, hestia/library/blueprints//*.yaml	| Reusable automation/script templates	| Non-portable entity IDs; schema drift	| Task: ADR-0024: Validate HA YAML & Core |
| Themes & Frontend YAML	| themes//*.yaml, domain/themes//.yaml, domain/frontend/.yaml	| UI appearance and frontend behavior	| Invalid color vars; non-existent resources	| Task: ADR-0024: Validate HA YAML & Core |
| HA SQL YAML + SQL	| domain/sql/**/*.yaml, **/*.sql	| SQL sensors and DB init	| Long-running queries; unindexed joins	| Task: ADR-0024: Validate HA YAML & Core |
| DevTools/Lovelace Templates	| hestia/library/templates/**/.{jinja,yaml}	| Diagnostics & dev-only templates	| Verbose output; template errors in DevTools	| Task: Hestia: Patch HA templates |
| Python Tools/CLIs	| hestia/tools//*.py, bin//*.py	| Repo tooling and validators	| Python <3.10 syntax; missing entrypoints	| Run: pytest (if present); lint via ruff (pyproject) |
| Prompts	| .github/prompts/**/*.prompt.md	| Copilot prompt definitions	| Non-compliant frontmatter; unsupported tools field	| Script: validate_frontmatter.py |
| ADR Docs	| hestia/library/docs/ADR/**/*.md	| Governance & rules	| Wrong ADR format; missing frontmatter	| Tool: adr-index.py |
| CI Workflows	| .github/workflows/**/*.yml	| GitHub Actions	| Secrets leakage; wrong paths	| GitHub Actions lint (optional) |
| HA Python Scripts	| python_scripts/**/*.py	| HA built-in python_scripts	| Unsupported libs; blocking operations	| HA config validate |
| JS/TS utilities	| **/*.{js,ts}	| Frontend/utility scripts	| Non-minified assets; path imports	| N/A |
| Hestia System Config	| hestia/config/**/*.{yaml,toml,ini,conf}	| System indices and configs	| Drift vs ADRs; path non-compliance	| Task: ADR-0024: Path Health |


## Governance links:

- Governance index: `governance_index.md`
- Instructions standard: `instructions.instructions.md`
- Copilot assistant guide: `copilot-instructions.md`
- Canonical config: `hestia.toml`

## top5_instructions/ (content only, ready to save under .github/instructions/)
1) `ha-packages.instructions.md`
