---
id: ADR-0010
title: "ADR-0010: Workspace Shape (amended by ADR-0016)"
date: 2025-09-11
status: Accepted
author:
  - "Evert Appels"
  - "Github Copilot"
related:
  - ADR-0008
  - ADR-0009
  - ADR-0011
  - ADR-0012
  - ADR-0013
  - ADR-0015
  - ADR-0016
supersedes: []
last_updated: 2025-09-25
author: 
  - "Evert Appels"
tags: ["/n/ha", "autofs", "workspace", "mount", "smb", "macos", "pathing", "folder-structure"]
amended_by: [ADR-0016]
notes: "Historical '/n/ha' reference retained in context; canonical path is ${HA_MOUNT:-$HOME/hass}."
---

# ADR-0010: Workspace Shape (amended by ADR-0016)

## Status
Accepted

## Context
Frequent path divergence (`/Volumes/HA` vs `/Volumes/ha`), fragile SMB mounts, and mixed tooling caused non-deterministic edits and outages. We need a single, neutral, reboot-resilient mount on macOS plus a portable pathing approach for cross-workspace tooling.

## Decision
1) **Neutral macOS path (operator convenience only):** On macOS, the Home Assistant `config` share is mounted at **`/n/ha`** via **autofs** (direct map in `/etc/auto_master` referencing `/etc/auto_smb`).

2) **Portability rule (scripts & docs):**
   - Repo **scripts/Makefiles** MUST NOT hardcode `/n/ha`. Use a parameterized root: `HA_ROOT` defaulting to `/config`.
     - Example: `ROOT="${HA_ROOT:-/config}"`.
   - Cross-platform docs use repo-relative or `/config` paths. `/n/ha` is permitted **only** in macOS-specific operator guides.
   - Canonical template entrypoint remains: `/config/custom_templates/template.library.jinja` (see ADR-0015).

3) **Canonical workspace shape:**
   - Tools, caches, and generated artifacts live inside the repo; no home-directory droppings.
   - Path usage is consistent across `core/`, `deploy/`, `docs/`, `tools/`, `work/`, `vault/` (see ADR-0012).

4) **Programmatic enforcement:**
   - `hestia/tools/system/hestia_workspace_enforcer.sh` fails pre-commit/CI if:
     - Any tracked file contains `'/Volumes/HA'` or `'/Volumes/ha'`.
     - **Portable** code paths hardcode `/n/ha` (allowlist macOS operator docs only).
     - `${HA_ROOT:-/config}` is not respected where a root is required.
   - CI checks that `/config/custom_templates/template.library.jinja` is referenced (not `/n/ha/...`) in portable code.

## Consequences
- Stable editing on macOS regardless of drive case or Finder behavior.
- Predictable CI and fewer path-related incidents.
- Clear separation between local operator convenience (`/n/ha`) and portable automation (`$HA_ROOT` / `/config`).

## Implementation
- `/etc/auto_master`: ensure a direct map, e.g.  
  `/-    auto_smb   -nosuid`
- `/etc/auto_smb`: provide a single active mapping to the HA `config` share, with commented fallbacks for `.local` and Tailscale:

## Accessing the Home Assistant Configuration Volume (Multi-Environment Policy)

This section standardizes how paths to the Home Assistant config volume are expressed across contexts. The goals are portability, determinism, and zero leakage of host-specific paths into portable code.

### Summary Matrix

| Context / Direction                      | Canonical Root to Use | Hardcode? | Parameter(s)                                      | Notes |
|-----------------------------------------|------------------------|-----------|---------------------------------------------------|-------|
| Inside HA (Supervisor/Container/Addon) | `/config`               | NO        | `HA_ROOT` (default `/config`)                     | Scripts/templates within HA treat `/config` as root. |
| Operator machine / other workspaces     | mounted HA share       | NO        | `HA_MOUNT` (default `/n/ha` on macOS), `HA_ROOT`  | Use variables; do not hardcode `/n/ha` in portable code. |
| Between mounted volumes (host ↔ host)   | explicit mounts        | NO        | `SRC_MOUNT`, `DST_MOUNT`                          | Never rely on `/Volumes/...` in automation; prefer autofs targets. |

Naming:
- `HA_ROOT` → semantic root of the HA config tree (defaults to `/config` when running in HA).
- `HA_MOUNT` → physical mountpoint on the operator host for the HA config share (defaults to `/n/ha` on macOS operator docs/scripts only).

### 1) Within the HA Environment (Supervisor / Add-ons / Containers)

Use `/config` exclusively. Do not reference host mounts from inside HA.

**DO**

```bash
ROOT="${HA_ROOT:-/config}"
test -f "$ROOT/configuration.yaml"
```

**DON'T**

```bash
# Anti-patterns inside HA:
ls /n/ha/configuration.yaml          # host-specific
ls /Volumes/HA/configuration.yaml    # host-specific
```

#### Jinja / YAML references

```yaml
!include_dir_merge_named /config/packages
```

### 2) From Other Workspaces (Operator Host, CI Runners, Tooling Outside HA)

Portable scripts must not hardcode platform paths. Use parameters and sane defaults.

#### Pattern:

```bash
# For tooling that may run inside or outside HA:
HA_ROOT="${HA_ROOT:-/config}"        # semantic root (inside HA)
HA_MOUNT="${HA_MOUNT:-/n/ha}"        # operator mount default (macOS docs only)

# Resolve an effective root for file operations:
if [ -d "$HA_ROOT" ] && [ -f "$HA_ROOT/configuration.yaml" ]; then
  EFFECTIVE="$HA_ROOT"               # running in/near HA
else
  EFFECTIVE="$HA_MOUNT"              # running on operator machine
fi

test -f "$EFFECTIVE/configuration.yaml"
```

#### References to the canonical template

```bash
TEMPLATE="${EFFECTIVE}/custom_templates/template.library.jinja"
```

**DON'T**

```bash
# Leaks a host default into portable code:
HA_MOUNT=/n/ha; cp /n/ha/configuration.yaml ./backup/
```

### 3) Between Mounted Volumes (e.g., `/Volumes/share` → HA, or HA → external share)

For automated transfers between two host mounts, never rely on `/Volumes/...` paths; these are brittle (case/space/GUI automount quirks). Prefer autofs targets and parametrization.

**DO**

```bash
SRC_MOUNT="${SRC_MOUNT:-/n/share}"           # your external share via autofs
DST_MOUNT="${DST_MOUNT:-${HA_MOUNT:-/n/ha}}" # HA mount

# Example: sync dashboards → HA
rsync -a --delete --protect-args \
  "${SRC_MOUNT}/ha_dashboards/" \
  "${DST_MOUNT}/lovelace/"
```

If you must interop with `/Volumes/...` (manual operator actions only):
- Quote paths with spaces.
- Do not commit such paths to scripts or docs outside macOS-specific operator guides.

**DON'T**

```bash
# Fragile and non-portable:
rsync -a "/Volumes/My Share/ha_dashboards/" "/Volumes/HA/lovelace/"
```

### Guardrails & Enforcement

- Portable code MUST parameterize roots:
  * `HA_ROOT` (default `/config`)
  * `HA_MOUNT` (default `/n/ha` for macOS operator docs only)
  * `SRC_MOUNT`, `DST_MOUNT` for cross-volume operations

- Banned in portable code (CI-enforced):
  - Hardcoded `/n/ha`
  - Any `/Volumes/...`

- Allowed locations for `/n/ha` mentions:
  - MacOS operator playbooks and runbooks only (e.g., `docs/playbooks/`).

- Canonical template path (for all contexts, via the resolved root):
  `${EFFECTIVE}/custom_templates/template.library.jinja`

## Token Blocks

```yaml
TOKEN_BLOCK:
  accepted:
    - PATH_POLICY_HA_CONFIG_OK
    - PORTABLE_PARAM_ROOTS_OK
  requires:
    - ADR_SCHEMA_V1
    - WORKSPACE_SHAPE_OK
  drift:
    - DRIFT: hardcoded_volumes_path
    - DRIFT: hardcoded_nha_in_portable_code
    - DRIFT: missing_root_parameters
    - DRIFT: canonical_template_path_incorrect
```

## Changelog

- 2025-09-11: Initial draft.
- 2025-09-12: Accepted draft; added enforcement and script details.
- 2025-09-25: De-emphasized “/n/ha” in ADR-0010’s title/summary.
