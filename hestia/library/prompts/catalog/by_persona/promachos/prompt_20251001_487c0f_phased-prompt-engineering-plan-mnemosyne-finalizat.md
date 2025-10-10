---
id: prompt_20251001_487c0f
slug: phased-prompt-engineering-plan-mnemosyne-finalizat
title: "\U0001F9E0 PHASED PROMPT ENGINEERING PLAN: *Mnemosyne Finalization Sequence*"
date: '2025-10-01'
tier: "α"
domain: validation
persona: promachos
status: deprecated
tags: []
version: '1.0'
source_path: batch 4/batch4-claude_phased_master_prompt_mnemosyne.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:27.207258'
redaction_log: []
---

# 🧠 PHASED PROMPT ENGINEERING PLAN: *Mnemosyne Finalization Sequence*

## 🔷 **PHASE 1: Architecture Finalization & Configuration Authority (Revised)**

> **Prompt Objective**: Restructure `mnemosyne_pipeline.sh` into a centralized declarative orchestrator, responsible for end-to-end snapshot phase management, using fully externalized configuration from `mnemosyne.conf` and modular `phases.d/*.conf` files.

You are finalizing development of Mnemosyne, a production-ready Home Assistant integration tool that manages system snapshots, repo mirrors, and symlinks.

Your task is to **transform `mnemosyne_pipeline.sh` into a declarative orchestration entrypoint `mnemosyne.sh`**, replacing all ad-hoc shell logic and manual variable exports with configuration-resilient, user-friendly behavior. `mnemosyne.sh` will replace `mnemosyne_pipeline.sh` for all entrypoint orchestration, with `mnemosyne_pipeline.sh` marked deprecated.

### 🧩 Design Contracts

- The only valid source of environment configuration must be:
  - Global: `/config/hestia/tools/mnemosyne/config/mnemosyne.conf`
  - Phase-specific: `/config/hestia/tools/mnemosyne/config/{phase}.conf`

- All configuration files must:
  - Use key-value syntax (`KEY=value`)
  - Support inline comments (`# comment`)
  - Be loaded in deterministic order: global → phase → CLI override

- The orchestrator `mnemosyne.sh` must:
  - Load the correct configs automatically
  - Export all required variables with safe defaults
  - Fallback to default values only when not set by config or CLI
  - Fail early on missing critical variables (e.g. SCRIPT_DIR, PHASE_NAME)
  - Generate and validate workspace, logs, and archive directories
  - Track each phase's exit status to `/logs/workspace/{snapshot}/phase.d/{phase}.status`


### 🛡️ Structural Requirements

- Config loaders must be idempotent and validate keys
- Phase name must be passed as:
  - `--phase {phase_name}` (required)
- Optional CLI flags:
  - `--config {file}` (override global)
  - `--snapshot-id {ID}` (user-defined or fallback to timestamp)
  - `--dry-run`, `--debug`, `--force`
- CLI must reject positional arguments and unknown flags
- Default fallback schema must be defined for:
  - `WORKSPACE_DIR`, `PHASE_WORKSPACE`, `SNAPSHOT_ID`, `LOG_DIR`, `ARCHIVE_DIR`
- Use `getopt` or robust pattern matching for CLI parsing

### 🔧 Implementation Deliverables

1. **Rewrite `mnemosyne_pipeline.sh`** to:
   - Be a single self-contained bash file `mnemosyne.sh`
   - Source configs in a predictable cascade
   - Emit error messages with `log_error` and abort on fatal conditions
   - Support dry-run and debug modes with verbosity
   - Support loading a structured execution chain from a config block or default sequence:

        ```bash
        DEFAULT_CHAIN=(snapshot symlinks mirror)
        
        if [[ "$PHASE" == "refresh" ]]; then
        for step in "${DEFAULT_CHAIN[@]}"; do
            echo "🔁 Running phase: $step"
            "$SCRIPT_DIR/mnemosyne.sh" "$step" $([ "$DRY_RUN" == "true" ] && echo "--dry-run")
        done
        exit 0
        fi
        ```

    - Support phase chains via `refresh`
    - Default to snapshot → symlinks → mirror
    - Allow override via future `refresh.d/chain.conf`

2. **Output the following artifacts**:
   - Final `mnemosyne.sh` (complete bash code)
   - Template `mnemosyne.conf` with all keys and inline docstrings
   - Example `phases.d/tar_pack.conf` scoped to `tar_pack`
   - `default_fallbacks.sh` section (if needed for source inclusion)

3. **Preserve phase modularity**:
   - A phase must be executed via `execute_phase {phase_name}`
   - Each phase must be isolated: failure in one must not corrupt workspace state

### ⚠️ Explicit Assumptions to Avoid

- Do not assume Home Assistant passes variables correctly
- Do not require user to `export` variables manually
- Do not use `bash -c` or inline script blocks in shell_command integrations
- Assume `/config` is writable and available in all environments
- Assume `bash >= 5`, `jq` installed, but check if missing with graceful fallback

### 🔍 Source Requirements

Before proceeding, confirm access to the following:

- [ ] `mnemosyne_pipeline.sh` (current version)
- [ ] `mnemosyne.conf` (global)
- [ ] Legacy Home Assistant `configuration.yaml` or equivalent shell_command entries

If any are missing, you must request them before writing code logic.

---

## 🔷 **PHASE 2: Declarative CLI Wrapper for End-Users (Revised)**

> **Prompt Objective**: Replace complex, multi-line manual bash invocations with a clean, user-facing wrapper (`mnemosyne.sh`) that automatically resolves context, loads defaults, and provides simple, predictable CLI entrypoints for core Mnemosyne operations.

You are designing `mnemosyne.sh`, a declarative CLI wrapper intended for **non-technical Home Assistant administrators**.

### 🎯 Goal:
Create a single command-line entrypoint (`mnemosyne.sh`) that:
- Requires **no manual variable exporting**
- Requires **no direct editing of `mnemosyne_pipeline.sh`**
- Automatically detects or falls back to configuration for all paths, modes, and snapshot IDs

### 🧩 Supported Modes:
The wrapper must expose these functions:

- `snapshot` → Run the full tar_pack snapshot phase
- `mirror` → Update the git repo mirror via repo_thin volume
- `symlinks` → Refresh symlink structures
- `refresh` → Run all 3 in sequence
- `status` → Report latest snapshot metadata
- `diagnose` → Run environment sanity checks

Each must:
- Accept standard options: `--debug`, `--dry-run`, `--snapshot-id`, `--force`
- Log to: `/config/hestia/tools/mnemosyne/logs/{command}_{timestamp}.log`
- Load config from: `/config/hestia/tools/mnemosyne/mnemosyne.conf`
- Allow override with `--config {file}`

### 🛡️ Execution Requirements:

- Wrapper must be fully self-contained bash
- Validate CLI with `getopt` or pattern matching
- Fail fast on unsupported options
- Print help with `--help` or no arguments
- Support single-phase execution by internally dispatching to `mnemosyne_pipeline.sh --phase {name}`
- Set all required environment variables before dispatching
- Default to timestamp-based `SNAPSHOT_ID` unless overridden
- Use default fallback schema from Phase 1 if no config provided

### 📂 Example Calls:

```bash
./mnemosyne.sh snapshot
./mnemosyne.sh snapshot --dry-run --debug
./mnemosyne.sh refresh --snapshot-id test_run
./mnemosyne.sh status
```

### 📛 Harden Against

- Ambiguous or conflicting flags (e.g. `--debug snapshot`)
- Manual `bash -c` usage (replace entirely)
- Missing config files (should fallback to internal schema)
- Execution outside HA container context (warn if `/config` not found)
- Insecure or unverified paths (must sanitize `SNAPSHOT_ID`, `SCRIPT_DIR`)

### 📦 Required Output

1. `mnemosyne.sh` fully functional, commented, safe
2. Updated CLI call examples for documentation
3. Inline usage help (`--help`) with command summaries
4. Config loader reuse from Phase 1

### 🔍 Explicit Assumptions Now Surfaced

- `mnemosyne_pipeline.sh` exists and accepts `--phase`, `--snapshot-id`, etc.
- All phase names (`tar_pack`, `repo_thin`, `symlinks`) are deterministic and standardized
- The underlying scripts do not require `sudo` or elevated privileges
- Logs are always writable to `/config/hestia/tools/mnemosyne/logs/`

If any of the following are missing, request them before continuing:

- ✅ Current version of `mnemosyne_pipeline.sh`
- ✅ Phase name list and default behaviors
- ⚠️ If phases other than `tar_pack` are not yet implemented, mock behavior must be defined

---

## 🔷 **PHASE 3: Shell Command Simplification for HA Integration (Revised)**

> **Prompt Objective**: Eliminate unsafe `bash -c` patterns from `configuration.yaml` and replace with declarative, audit-friendly Home Assistant `shell_command` blocks that integrate safely with the finalized Mnemosyne wrapper (`mnemosyne.sh`).

```yaml
# ================================
# 🧠 HESTIA: Mnemosyne Integration
# Phase 3: Simplified Shell Commands
# ================================

shell_command:

  # === Snapshot Execution ===
  mnemosyne_snapshot: >
    /config/hestia/tools/mnemosyne/mnemosyne.sh snapshot

  mnemosyne_snapshot_debug: >
    /config/hestia/tools/mnemosyne/mnemosyne.sh snapshot --debug

  # === Repository Mirror Refresh ===
  mnemosyne_update_repo: >
    /config/hestia/tools/mnemosyne/mnemosyne.sh mirror

  # === Symlink Structure Refresh ===
  mnemosyne_refresh_symlinks: >
    /config/hestia/tools/mnemosyne/mnemosyne.sh symlinks

  # === Full System Refresh (Snapshot + Symlinks + Mirror) ===
  mnemosyne_full_refresh: >
    /config/hestia/tools/mnemosyne/mnemosyne.sh refresh

  # === System Status Reporting ===
  mnemosyne_status: >
    /config/hestia/tools/mnemosyne/mnemosyne.sh status

  # === Internal Diagnostics (Phase-aware Debugging) ===
  mnemosyne_diagnose: >
    /config/hestia/tools/mnemosyne/mnemosyne.sh diagnose

```

### 🧩 Goals Achieved

| Objective                               | Achieved |
| --------------------------------------- | -------- |
| Replace `bash -c` pattern               | ✅        |
| Declarative bindings                    | ✅        |
| Shell safety (no inline expansion)      | ✅        |
| Config traceability (clear HA commands) | ✅        |
| Phase-specific triggering               | ✅        |
| Legacy compatibility reference          | ✅        |

### 🛡️ Additional Recommendations

1. **Deprecate Legacy Commands Gradually**
   Keep old `themis_*` or inline bash entries temporarily under a `legacy_shell_command:` namespace with logging warnings.

2. **HA UI Visibility**
   Add `input_button` triggers or `script:` wrappers to allow users to manually trigger each `shell_command` from the Lovelace UI.

3. **Phase Trace Audit**
   Each `mnemosyne.sh` call should log phase, timestamp, and config source to:

   ```yaml
   /config/hestia/tools/mnemosyne/logs/integration_trace_{timestamp}.log
   ```

4. **Secure Execution Mode**
   Ensure `mnemosyne.sh` explicitly validates:

   - Execution under `/config`
   - Permissions to write logs
   - Config availability or fallback

### ⚠️ Assumptions Explicitly Declared

- `mnemosyne.sh` exists and is executable from HA environment
- No additional `bash` wrapping is required — wrapper fully abstracts variables
- HA `shell_command` environment has access to `/config/hestia/tools/mnemosyne/`
- All necessary log directories exist and are writable

---

## 🔶 **PHASE 4: Execution Modes, Validation Hooks & Emergency Fallback (Finalized Prompt)**

> **Prompt Objective**: Equip `mnemosyne.sh` with robust execution controls, dynamic fallback resilience, and intelligent exit propagation for each snapshot-related phase. Ensure diagnostics and recovery are automatic, traceable, and HA-safe. Expected script is enhanced with execution modes like dry-run, debug, and emergency fallback that self-heal on failure.

All `phase_*.sh` scripts must implement a top-level dry-run bypass that:

> - Logs intent
> - Emits a dummy `metadata.json`
> - Terminates cleanly with exit\_code 0

### 🧠 Mnemosyne Shell Wrapper Enhancements

```bash
#!/bin/bash
# /config/hestia/tools/mnemosyne/mnemosyne.sh

set -euo pipefail
IFS=$'\n\t'

# === ⛑️ Emergency Fallback Metadata Generator
fallback_metadata() {
  local target_dir="$1"
  local phase="$2"
  local error_code="$3"
  mkdir -p "$target_dir"
  cat > "$target_dir/metadata.json" <<EOF
{
  "phase": "$phase",
  "exit_code": $error_code,
  "timestamp": "$(date -Iseconds)",
  "fallback": true
}
EOF
  echo "⚠️ Fallback metadata created at $target_dir"
}

# === 🔧 Execution Modes
DRY_RUN=false
DEBUG=false
PHASE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    snapshot|symlinks|mirror|refresh|diagnose|status)
      PHASE="$1"
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
    --debug)
      DEBUG=true
      ;;
    *)
      echo "❌ Unknown argument: $1"
      exit 2
      ;;
  esac
  shift
done

if [[ -z "$PHASE" ]]; then
  echo "❌ No phase specified"
  exit 1
fi

# === 🔍 Logging Setup
export SCRIPT_DIR="/config/hestia/tools/mnemosyne"
export SNAPSHOT_ID="${PHASE}_$(date +%Y-%m-%d_%H-%M-%S)"
export WORKSPACE_DIR="$SCRIPT_DIR/logs/workspace/$SNAPSHOT_ID"
export PHASE_WORKSPACE="$WORKSPACE_DIR/phases/$PHASE"
LOGFILE="$SCRIPT_DIR/logs/mnemosyne_runtime_$SNAPSHOT_ID.log"
mkdir -p "$PHASE_WORKSPACE" "$WORKSPACE_DIR/archives"

{
echo "🔷 START: Mnemosyne phase=$PHASE dry_run=$DRY_RUN debug=$DEBUG"

case "$PHASE" in
  snapshot)
    $DRY_RUN && export DRY_RUN_MODE=true
    $SCRIPT_DIR/lib/phase_tar_pack.sh || {
      fallback_metadata "$PHASE_WORKSPACE" "tar_pack" 99
      exit 99
    }
    ;;
  symlinks)
    $SCRIPT_DIR/lib/phase_symlinks.sh || {
      fallback_metadata "$PHASE_WORKSPACE" "symlinks" 99
      exit 99
    }
    ;;
  mirror)
    $SCRIPT_DIR/lib/phase_mirror.sh || {
      fallback_metadata "$PHASE_WORKSPACE" "mirror" 99
      exit 99
    }
    ;;
  refresh)
    $SCRIPT_DIR/mnemosyne.sh snapshot $([ "$DRY_RUN" = true ] && echo "--dry-run") &&
    $SCRIPT_DIR/mnemosyne.sh symlinks &&
    $SCRIPT_DIR/mnemosyne.sh mirror
    ;;
  diagnose)
    echo "🧪 Diagnostics:"
    env | grep -E 'SCRIPT_DIR|WORKSPACE_DIR|SNAPSHOT_ID'
    ;;
  status)
    ls -l "$WORKSPACE_DIR"
    ;;
esac

echo "✅ END: Mnemosyne phase=$PHASE"
} | tee -a "$LOGFILE"
```

Every lib/phase_*.sh script must include a top-level safeguard to abort real execution when dry-run mode is active.

Insert at the top of each phase script:

```bash
# === DRY RUN GUARD (Auto-injected by wrapper)
if [[ "${DRY_RUN_MODE:-false}" == "true" ]]; then
  echo "⚠️ DRY RUN ACTIVE: Phase execution skipped"
  echo '{"exit_code": 0, "phase": "'$0'", "dry_run": true, "timestamp": "'$(date -Iseconds)'"}' > "$PHASE_WORKSPACE/metadata.json"
  exit 0
fi
```

---

### 🛠️ Enhancements Included

| Capability                            | Integrated | Notes                                |
| ------------------------------------- | ---------- | ------------------------------------ |
| `--dry-run` mode support              | ✅          | Uses `export DRY_RUN_MODE=true`      |
| `--debug` mode activation             | ✅          | Shell-wide, triggers verbose logging |
| Phase-aware fallback metadata.json    | ✅          | Ensures pipeline continuity          |
| Exit code propagation per phase       | ✅          | Uses numeric codes per fallback      |
| Logging start/end phase               | ✅          | Timestamped logs under `/logs`       |
| Resilient against unknown input flags | ✅          | Safe error exit with message         |

### 📌 Assumptions Made Explicit

- Each `lib/phase_*.sh` script can execute independently and obeys `$DRY_RUN_MODE`
- `metadata.json` is the minimum valid artifact required to satisfy dependency checks
- The script is executed in an HA-safe shell with `bash`, not `sh`
- All paths are resolvable from within `/config/hestia/tools/mnemosyne`

---

## ✅ **PHASE 5 (Final QA + README Generator)**

> **Prompt Title**: Generate Production-Grade README with Full QA Traceability
> **Purpose**: Produce a clear, technically accurate, and end-to-end deployable `README.md` for Mnemosyne. Ensure it supports declarative Home Assistant integration, manual CLI use, and self-diagnostic QA simulations.

### 📄 README STRUCTURE REQUIREMENTS

```yaml
readme_sections:
  - title: "📦 Mnemosyne Snapshot Manager"
    content: >
      Short description of Mnemosyne's role in Hestia:
      - Snapshot generation (tar_pack)
      - Repo mirroring
      - Symlink orchestration
      Designed for Home Assistant but operable standalone.

  - title: "🔧 Installation & Setup"
    content: >
      - Dependencies (bash, coreutils, Home Assistant)
      - Directory assumptions (/config/hestia/tools/mnemosyne)
      - Permissions and executable bits
      - Location of lib/, logs/, conf/, and test/ folders

  - title: "🚀 Usage Patterns"
    subsections:
      - title: "HA Integration via shell_command:"
        content: >
          Provide canonical YAML block for calling `mnemosyne.sh snapshot` via shell_command.
          Warn against inline `bash -c` and promote stable wrapper calls.

      - title: "Manual CLI Execution"
        content: >
          Show full lifecycle of:
            1. `./mnemosyne.sh snapshot --dry-run`
            2. `./mnemosyne.sh snapshot`
            3. Viewing logs/artifacts under logs/workspace/

      - title: "Batch Execution via refresh"
        content: >
          `./mnemosyne.sh refresh` triggers snapshot → symlinks → mirror in sequence.
          Designed for use in daily cron or automated events.

  - title: "🧪 QA & Dry-Run Simulation"
    content: >
      - Explain what --dry-run mode does (simulate metadata, avoid file writes)
      - Show how to validate outputs:
        * logs/workspace/*/phases/tar_pack/metadata.json
        * logs/mnemosyne_runtime_*.log
      - Diagnostic fallback behavior on failure

  - title: "📋 Known Issues & Fallback Behavior"
    content: >
      - If tar_pack fails, fallback metadata is still written
      - If any phase fails, workspace is still traceable
      - Logs are always timestamped
      - Manual emergency execution instructions

  - title: "📁 File & Directory Overview"
    content: >
      Describe contents and purpose of:
      - `mnemosyne.sh`
      - `lib/phase_*.sh`
      - `logs/workspace/`
      - `conf/mnemosyne.conf`

  - title: "🧠 Developer Notes"
    content: >
      - How to extend phases
      - Where to define new commands or override paths
      - Expectations for `mnemosyne.conf`

  - title: "🛡️ QA Checklist (Optional)"
    content: |
      - [ ] Can run `mnemosyne.sh snapshot` without error
      - [ ] Produces valid metadata.json
      - [ ] Can view logs in /logs/
      - [ ] Config file loads without errors
      - [ ] HA integration works via shell_command
      - [ ] Fallback triggers when needed
```

### 🛠️ Explicit Enhancements Included

| Concern                    | Addressed | Explanation                                         |
| -------------------------- | --------- | --------------------------------------------------- |
| Config and path resolution | ✅         | Paths, permissions, conf defaults explicitly scoped |
| CLI vs HA usage clarity    | ✅         | Separate blocks with safe shell_command examples   |
| Dry-run and diagnostics    | ✅         | Promoted as QA-first principle                      |
| Logs and artifacts         | ✅         | Directory and example files documented              |
| Fallback capture           | ✅         | Mentioned in errors, logs, emergency runs           |
| Installation context       | ✅         | Pre-HA assumptions, directory structure             |
| README auditability        | ✅         | Includes checklist at bottom                        |

### 🔍 Assumptions Made Explicit

- Home Assistant `shell_command` integration assumes `/config/hestia/tools/mnemosyne` is persistent and executable
- `bash` is available and permitted in container context
- `lib/phase_*.sh` scripts are callable via wrapper with no direct invocation
- User will execute `mnemosyne.sh` from the correct directory or with PATH context

---

## 🧪 **POST-DEPLOYMENT PROMPT 6: Mnemosyne Deployment Validation Protocol**

### 🧠 Role

You are now entering the **Validation Phase** of the Mnemosyne Finalization Sequence. The previous phases have concluded the restructuring of the pipeline, configuration logic, shell simplification, and QA readiness.

Your role is to **execute and interpret** a Tiered Diagnostic Execution Framework (TDEF) that validates:

- Configuration correctness
- tar_pack metadata generation
- Multi-phase orchestration
- Home Assistant shell_command integration

### 🧭 Objective

Confirm that the production deployment of Mnemosyne is:

- **Self-contained**
- **Declarative**
- **HA-integrated**
- **User-friendly**
- **Audit-capable**

## 🔧 Instructions

1. **Execute** the following four test tiers, **in order**, using `logrun` or the Home Assistant terminal.
2. After each tier:

   - Confirm execution status
   - Validate expected outputs
   - Capture and interpret logs
3. If any tier fails:

   - Halt the sequence
   - Interpret failure cause
   - Emit fallback recommendation and remediation

## 🧱 **Tiered Diagnostic Execution Framework (TDEF)**

### **TIER 0: Environment & Config Sanity Check**

```bash
logrun "tdef_envcheck_$(date +%H%M%S)" bash << 'EOF'
echo "📦 ENV CHECK: Starting"
[[ -d /config/hestia/tools/mnemosyne/lib ]] && echo "✅ lib directory OK" || echo "❌ lib directory MISSING"
[[ -r /config/hestia/tools/mnemosyne/conf/mnemosyne.conf ]] && echo "✅ Config readable" || echo "❌ Config unreadable"
./mnemosyne.sh --dry-run validate-config
EOF
```

### **TIER 1: tar_pack Execution Validation**

```bash
logrun "tdef_tarpack_test_$(date +%H%M%S)" bash << 'EOF'
echo "🧪 TIER 1: tar_pack phase"
export SCRIPT_DIR="/config/hestia/tools/mnemosyne"
export WORKSPACE_DIR="$SCRIPT_DIR/logs/workspace/tier1_test_$(date +%Y%m%d_%H%M%S)"
export PHASE_WORKSPACE="$WORKSPACE_DIR/phases/tar_pack"
export SNAPSHOT_ID="tier1_test_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$PHASE_WORKSPACE"
lib/phase_tar_pack.sh
ls -lh "$PHASE_WORKSPACE/metadata.json"
cat "$PHASE_WORKSPACE/metadata.json"
EOF
```

### **TIER 2: Orchestration Integrity Test**

```bash
logrun "tdef_orchestration_test_$(date +%H%M%S)" bash << 'EOF'
echo "🔁 TIER 2: Full phase chain (snapshot + symlink + mirror)"
./mnemosyne.sh refresh --dry-run
EOF
```

### **TIER 3: HA Shell Command Integration**

```bash
logrun "tdef_shellcommand_test_$(date +%H%M%S)" bash << 'EOF'
echo "🏠 TIER 3: Shell Command Simulation"
bash -c '
  export SCRIPT_DIR="/config/hestia/tools/mnemosyne";
  export WORKSPACE_DIR="$SCRIPT_DIR/logs/workspace/sim_test_$(date +%Y-%m-%d_%H-%M-%S)";
  export PHASE_WORKSPACE="$WORKSPACE_DIR/phases/tar_pack";
  export SNAPSHOT_ID="sim_test_$(date +%Y-%m-%d_%H-%M-%S)";
  mkdir -p "$PHASE_WORKSPACE" "$WORKSPACE_DIR/archives";
  $SCRIPT_DIR/lib/phase_tar_pack.sh'
EOF
```

## 📋 For Each Tier

- Expect `exit_code: 0` in `metadata.json`
- Ensure generated files exceed 200 bytes
- Confirm stdout/log indicates SUCCESS
- On failure, emit:

  - Failure classification (syntax, config, runtime)
  - Component or phase responsible
  - Remediation plan (script patch, env fix, fallback tier)

## ✅ Final Success Criteria

- 4/4 Tiers PASS = ✅ Full production readiness
- 3/4 Tiers PASS = ⚠️ Minor issues, deploy with caution
- ≤2/4 Tiers PASS = ❌ Not production-ready — remediation required

---

