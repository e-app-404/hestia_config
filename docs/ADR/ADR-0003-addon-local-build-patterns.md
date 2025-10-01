---
id: ADR-0003
title: "Home Assistant Add-on Local Build & Slug Management"
date: 2025-08-24
status: Accepted
author:
  - Promachos Governance
related: ["ADR-0001", "ADR-0002", "ADR-0008"]
supersedes: []
last_updated: 2025-08-24
---

# ADR-0003: Home Assistant Add-on Local Build & Slug Management

## Table of Contents
1. Context
2. Rules & Patterns
   - Add-on Folder Naming
   - Slug Field in config.yaml
   - Supervisor Slug Resolution
   - Required Files
   - config.yaml: Required Keys
   - Image Tagging
   - Add-on Lifecycle Commands
   - Troubleshooting
3. Expectations

## Context
Home Assistant Supervisor manages local add-ons using a combination of folder names and `config.yaml` fields. Correct configuration is essential for local builds, image tagging, and add-on lifecycle management.

## Rules & Patterns

### 1. Add-on Folder Naming
- Local add-ons reside in `/addons/local/<slug>`.
- The folder basename equals the `slug:` in `config.yaml`.  
  Example: folder `/addons/local/beep_boop_bb8` with `slug: "beep_boop_bb8"`.
  Supervisor addresses it as `local_beep_boop_bb8` in CLI commands.

### 2. Slug Field in config.yaml
- The `slug:` field matches the folder name **without** the `local_` prefix.
  ```yaml
  slug: "beep_boop_bb8"
  ```

### 3. Supervisor Slug Resolution
- Supervisor uses the folder name as the slug for local add-ons.
- If the folder is `/addons/local/beep_boop_bb8`, the slug is `local_beep_boop_bb8`.
- All Supervisor CLI commands must use the resolved slug.

### 4. Required Files
- Each add-on folder must contain at least:
  - `config.yaml`
  - `Dockerfile`
  - Entry script (e.g., `run.sh`)
  - App source files

### 5. config.yaml: Required Keys (mode-aware)
- Always: `name`, `slug`, `version`, `arch`, `init`.
- **LOCAL_DEV**: `image:` **absent** (commented); `Dockerfile` present.
- **PUBLISH**: `image:` **present** and `version:` equals the published tag.
- Example:
  ```yaml
  build:
    dockerfile: Dockerfile
    args:
      BUILD_FROM: "ghcr.io/home-assistant/{arch}-base-debian:bookworm"
  ```

### 6. Image Tagging
- **LOCAL_DEV**: `image:` absent; Supervisor builds locally from `Dockerfile`.
- **PUBLISH**: `image:` set to your registry reference (e.g., `ghcr.io/<org>/ha-bb8-{arch}`) and `version:` equals the pushed tag.

### 7. Add-on Lifecycle Commands
- Use the **resolved local slug** in Supervisor commands (prefix `local_`):
  ```bash
  ssh babylon-babes@homeassistant "ha addons reload"
  ssh babylon-babes@homeassistant "ha addons rebuild local_beep_boop_bb8"
  ssh babylon-babes@homeassistant "ha addons start local_beep_boop_bb8"
  ha addons logs local_beep_boop_bb8
  ```

### 8. Troubleshooting
- If Supervisor cannot find the add-on, check:
  - Folder name matches `slug:`
  - All required files exist
  - Run `ssh babylon-babes@homeassistant "ha addons reload"` after changes
  - Use `ha addons list` to confirm slug


## Expectations
- Consistent folder and slug naming prevents Supervisor errors.
- Always reload add-ons after changes to local add-on folders or config.
- Use the exact slug shown in `ha addons list` for all commands.

## Token Blocks

```yaml
TOKEN_BLOCK:
  accepted:
    - LOCAL_BUILD_OK
    - SLUG_MATCH_OK
    - SUPERVISOR_COMMAND_OK
  drift:
    - DRIFT: slug_mismatch
    - DRIFT: missing_required_files
    - DRIFT: supervisor_command_failed
```
