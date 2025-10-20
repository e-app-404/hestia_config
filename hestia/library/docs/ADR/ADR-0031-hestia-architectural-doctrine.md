---
id: ADR-0031
title: ADR-0031: Hestia Architectural Doctrine — Config-Centric Tooling (TOML-first)
slug: hestia-architectural-doctrine-config-centric-tooling-toml-first
status: Accepted
related:
    - ADR-0008
    - ADR-0015
    - ADR-0019
    - ADR-0023
    - ADR-0024
    - ADR-0027
    - ADR-0028
supersedes: []
last_updated: '2025-10-20'
date: 2025-10-20
decision: Formalize TOML-first, config-centric doctrine for all Hestia tools; require dynamic path resolution, dry-run/apply, governed writes, and canonical reporting/ledger structure.
author: Strategos (Executive Project Strategist)
tags: ["doctrine", "config-centric", "toml", "governance", "automation", "hestia", "development", "tools"]
---

# ADR-0031: Hestia Architectural Doctrine — Config-Centric Tooling (TOML-first)

## Table of Contents

1. [Context](#1-context)
2. [Decision](#2-decision)
3. [Architectural Tenets (for machine-operators)](#3-architectural-tenets-for-machine-operators)
4. [Standards & Style (checklist)](#4-standards--style-checklist)
5. [Implementation Guidance (Python)](#5-implementation-guidance-python)
6. [Migration & Backwards Compatibility](#6-migration--backwards-compatibility)
7. [Risks & Mitigations](#7-risks--mitigations)
8. [Acceptance Criteria](#8-acceptance-criteria)
9. [Worked Example — Folding “Glances → HA via Tailscale” into Doctrine](#9-worked-example--folding-glances--ha-via-tailscale-into-doctrine)
10. [Revisit Plan](#10-revisit-plan)
11. [Decision Summary (one-screen)](#11-decision-summary-one-screen)

## 1. Context

Hestia has evolved multiple operator tools (e.g., **sweeper**, **lineage-guardian**, **write-broker**, **meta_capture**). The common success pattern across these efforts:

- **Configuration lives in one place** (TOML block in `hestia.toml`).
- Tools **discover and resolve paths dynamically**; they do not hard-code absolute locations.
- All actions are **evidence-rich** (JSON reports, JSONL ledgers, logs) and **governed** (green-only apply, atomic writes, pin-locks, secret/schema checks).
- Outputs fold into a **shared reporting/indexing substrate** for auditability and downstream automation (HA sensors, CI, alerts).

We now formalize this doctrine so that **machine-operators** can construct new code that is compatible and mutually beneficial by default.

> **Note on scope**: This decision holds **only** while it benefits Hestia. Revisit if cargo-cult overhead outweighs value or the platform’s needs change.

## 2. Decision

1. **TOML-First Centralization**

     - All tooling (scripts, CLIs, services) MUST read runtime configuration from `hestia/config/system/hestia.toml` under a dedicated block (e.g., `[automation.<tool>]`).
     - **Do not hard-code absolute paths** in code. Resolve via TOML keys.
     - `.env` is reserved for **HA runtime** needs; **meta-tooling MUST NOT depend on `.env`** (may read as *last-resort fallback keys* only if explicitly stated).

2. **Standard Execution Model**
     Every tool provides **two modes**:

     - `dry-run`: discover inputs, validate, classify, **no writes**; produce **report** + **ledger**.
     - `apply`: **green-only** side effects; governed writes (atomic or via **write-broker**); update report + ledger.

3. **Governance & Safety Gates**

     - **Run-lock**, **idempotency**, **limits** (files/APUs), **secret & schema checks**, **pin-lock** (`# @pin`), **routing suggestions** for non-conforming inputs.
     - **Atomic writes** with `.bak` on overwrite; prefer **write-broker** when configured.
     - **Evidence**: human JSON report + JSONL ledger lines with `severity_counts`, `skip_reason`, broker evidence, APU objects.

4. **Canonical Paths & Hygiene**

     - Follow ADR-0024: canonical root is `/config`.
     - Reports → `/config/hestia/workspace/reports/<tool>/…`
     - Ledgers → `/config/hestia/workspace/.hestia/index/<tool>__index.jsonl`
     - Ops logs → `/config/hestia/workspace/operations/logs/<tool>/…`
     - Locks → `/config/hestia/workspace/.locks/…`
     - **No tracked symlinks** (ADR-0015). CI/CLI must guard this.

5. **Operator- and CI-Ready**

     - Provide **CLI bindings** (in `cli.conf`) and convenience Make targets.
     - CI uses **dry-run** with **policy gates** (zero-red; optional zero-orange per TOML `fail_level`).

## 3. Architectural Tenets (for machine-operators)

- **Single Source of Truth**: Configuration keys originate from `hestia.toml`. Tools must *fail* if required keys are absent (offer a `—print-sample-config` for onboarding).
- **Deterministic Discovery**: Inputs discovered via TOML glob lists; avoid shell-fragile patterns.
- **Idempotency by Design**: Skip identical work using content hashes / last-applied SHA from the ledger.
- **Green-Only Apply**: If classification is red/orange → do not write. Provide **routing_suggestion** for orange.
- **Atomicity & Broker**: Default atomic write with `.bak`; prefer `write-broker` integration when `[...apply.use_write_broker]=true`.
- **Observability**: Emit JSON report + JSONL ledger (**never** only STDOUT). Include **APU** object with provenance and safety checks.
- **Retention**: Obey `[...retention]` to prune reports and cap ledger lines.
- **Path Compliance**: Enforce ADR-0024 via a linter; fail on legacy `/config/hestia/core/config` references.
- **No Hidden State**: All tool state is in the ledger or report. No ad-hoc temp state outside `/config/hestia/workspace`.

## 4. Standards & Style (checklist)

- **Config block** in `hestia.toml`:

    ```toml
    [automation.<tool>]
    repo_root   = "/config"
    config_root = "/config/hestia/config"
    allowed_root= "/config/hestia"
    report_dir  = "/config/hestia/workspace/reports/<tool>"
    index_dir   = "/config/hestia/workspace/.hestia/index"
    secrets.rules = "/config/hestia/tools/<tool>/secret_rules.yaml"
    merge.policy  = "/config/hestia/tools/<tool>/merge_policy.yaml"

    [automation.<tool>.paths]
    jsonl_index = "/config/hestia/workspace/.hestia/index/<tool>__index.jsonl"
    routing_template = "/config/hestia/tools/<tool>/routing_suggestions_template.yaml"

    [automation.<tool>.limits]
    max_files     = 100
    max_apus      = 2000
    oversize_bytes= 5_000_000
    fail_level    = "red"  # or "orange"

    [automation.<tool>.apply]
    use_write_broker = true
    write_broker_cmd = "/config/bin/write-broker"
    write_broker_mode= ""  # auto-detect rewrite/replace

    [automation.<tool>.retention]
    reports_days = 14
    ledger_lines = 20000
    ```

- **CLI bindings** (`cli.conf`):

    ```yaml
    <tool>:
        dry_run:  "/config/hestia/tools/<tool>/<tool>.py dry-run --inputs ..."
        apply:    "/config/hestia/tools/<tool>/<tool>.py apply --inputs ..."
        prune_reports: "find /config/hestia/workspace/reports/<tool> -type f -mtime +14 -delete"
        prune_ledger:  "tail -n 20000 /config/hestia/workspace/.hestia/index/<tool>__index.jsonl > tmp && mv tmp /config/hestia/workspace/.hestia/index/<tool>__index.jsonl"
    ```

- **Outputs** (must exist after each run):

    - `…/__<ts>__dry_run.json` or `…/__<ts>__apply.json` (human JSON report)
    - `…/<tool>__index.jsonl` (append-only ledger)

- **Error Classes** (examples):
    `E-LOCK-001` (run-lock), `E-PIN-LOCK-001`, `E-SECRETS-xxx`, `E-SCHEMA-xxx`, `E-BROKER-001`, `E-LIMIT-APU-001`, `E-PATH-ADR0024`.

## 5. Implementation Guidance (Python)

**Config loader**

```python
# py311+: use tomllib; older: fall back to tomli
try:
        import tomllib as toml
except Exception:  # pragma: no cover
        import tomli as toml

from pathlib import Path

def load_cfg(tool: str):
        htoml = Path("/config/hestia/config/system/hestia.toml")
        data = toml.loads(htoml.read_text(encoding="utf-8"))
        cfg = data.get("automation", {}).get(tool)
        if not cfg:
                raise SystemExit(f"E-CONFIG: missing [automation.{tool}] in {htoml}")
        return cfg
```

**Run-lock & idempotency**

```python
import fcntl, hashlib, json, time

def acquire_lock(lockfile: Path):
        lockfile.parent.mkdir(parents=True, exist_ok=True)
        fp = lockfile.open("w")
        try:
                fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
                raise SystemExit("E-LOCK-001: another run is in progress")
        return fp  # keep open

def sha256_bytes(b: bytes) -> str:
        h = hashlib.sha256(); h.update(b); return h.hexdigest()

def last_applied_sha(index: Path, target: str) -> str | None:
        if not index.exists(): return None
        with index.open("r", encoding="utf-8") as fh:
                for line in reversed(fh.readlines()[-5000:]):  # tail window
                        try:
                                d = json.loads(line)
                                for r in d.get("results", []):
                                        if r.get("target_path") == target and r.get("applied") and r.get("apu", {}).get("provenance", {}).get("sha256"):
                                                return r["apu"]["provenance"]["sha256"]
                        except Exception:
                                continue
        return None
```

**Atomic write + broker**

```python
import os, subprocess, tempfile

def atomic_write_text(dst: Path, text: str):
        tmp = Path(tempfile.mkstemp(prefix=dst.name, dir=str(dst.parent))[1])
        tmp.write_text(text, encoding="utf-8")
        bak = dst.with_suffix(dst.suffix + ".bak") if dst.exists() else None
        if bak: dst.replace(bak)
        tmp.replace(dst)

def broker_rewrite(cfg_apply: dict, dst: Path, temp_src: Path) -> tuple[int, str, str]:
        cmd = cfg_apply.get("write_broker_cmd")
        if not cmd: return (127, "", "broker_not_configured")
        mode = cfg_apply.get("write_broker_mode", "")
        args = [cmd, mode or "rewrite", "--file", str(dst), "--from", str(temp_src)]
        p = subprocess.run(args, capture_output=True, text=True)
        return (p.returncode, p.stdout[-4000:], p.stderr[-4000:])
```

**Report & ledger emission**

```python
from datetime import datetime, UTC

def now_z(): return datetime.now(UTC).isoformat().replace("+00:00","Z")

def append_ledger(index: Path, payload: dict):
        index.parent.mkdir(parents=True, exist_ok=True)
        with index.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload, separators=(",",":")) + "\n")
```

## 6. Migration & Backwards Compatibility

- **Paths**: Replace legacy `/config/hestia/core/config/` with `/config/hestia/config/` (ADR-0024). A linter step MUST fail on old paths.
- **Existing tools**:

    - **sweeper**, **lineage-guardian**, **write-broker**, **meta_capture** already follow most tenets; ensure each reads from `hestia.toml` and writes reports/ledgers to the canonical locations.
- **Phased adoption**: New tooling MUST follow this ADR. Existing scripts SHOULD be refactored when touched.

## 7. Risks & Mitigations

- **Overhead for small scripts** → Provide a **tiny scaffold** (loader/ledger/lock) so overhead is <50 lines.
- **Stale TOML keys** → CI checks for required keys per tool.
- **Operator bypass** → CLI/Make/VSCode tasks standardize run paths; documentation emphasizes dry-run first.
- **Write safety** → Broker + atomic write + `.bak` + idempotency reduce blast radius.

## 8. Acceptance Criteria

- New tool PRs include:

    - `[automation.<tool>]` block in `hestia.toml`, CLI wiring, dry-run & apply, report + ledger, run-lock, idempotency, secret/schema checks, optional broker, retention knobs.
- CI:

    - **Zero-red** enforcement on dry-run; orange enforcement if `fail_level="orange"`.
    - ADR-0024 path compliance linter passes.
    - No tracked symlinks (ADR-0015).

## 9. Worked Example — Folding “Glances → HA via Tailscale” into Doctrine

**Petition**: A standalone shell + Python proxy (`glances-normalize.py`) to normalize Glances API and expose via Tailscale.

**Doctrine-compliant plan**:

1. **Create tool**: `/config/hestia/tools/glances_bridge/` with `glances_bridge.py`, schemas, secret rules, merge policy.

2. **hestia.toml** (excerpt):

     ```toml
     [automation.glances_bridge]
     repo_root   = "/config"
     config_root = "/config/hestia/config"
     allowed_root= "/config/hestia"
     report_dir  = "/config/hestia/workspace/reports/glances_bridge"
     index_dir   = "/config/hestia/workspace/.hestia/index"

     [automation.glances_bridge.runtime]
     upstream_url    = "http://127.0.0.1:61208"
     listen_host     = "127.0.0.1"
     normalizer_port = 61209
     tailscale_host  = "macbook.reverse-beta.ts.net"
     tailscale_port  = 61208

     [automation.glances_bridge.apply]
     use_write_broker = true
     write_broker_cmd = "/config/bin/write-broker"
     write_broker_mode= ""

     [automation.glances_bridge.retention]
     reports_days = 14
     ledger_lines = 20000
     ```

3. **`glances_bridge.py`** provides `dry-run` (probe upstream, simulate normalize) & `apply` (spawn/daemonize proxy, configure `tailscale serve`), emitting:

     - `…/reports/glances_bridge/*__dry_run.json|__apply.json`
     - `…/.hestia/index/glances_bridge__index.jsonl`
         with **APU** objects and **broker evidence**.

4. **HA Integration**: Use HA RESTful sensors to read **normalized** endpoint (tailscale URL); feed anomalies to Hestia’s reports for alerting.

5. **Governance**: Pin-locks on critical TOML keys (e.g., ports) with `# @pin`. Secret rules scan logs for accidental token leaks.

6. **Retirement of the raw script**: Keep the existing shell block as an **operator bootstrap** that calls `glances_bridge.py apply` using values from TOML (no inline variables).

This turns a niche script into a **first-class governed tool** that benefits from Hestia’s shared observability and safety mechanisms.

## 10. Revisit Plan

- Reassess this ADR **every 6 months** or upon evidence of undue overhead.
- Sunset or relax elements (e.g., broker requirement) when platform changes justify it.

## 11. Decision Summary (one-screen)

- **Use `hestia.toml`** as the single configuration source.
- **No hard-coded paths**; resolve via TOML.
- **dry-run/apply** with **green-only apply**.
- **Run-lock, idempotency, limits, secrets/schema, pin-lock**.
- **Atomic writes / write-broker**, `.bak` on overwrite.
- **Reports + JSONL ledgers** in canonical locations.
- **ADR-0024/0015 compliance** enforced in CLI/CI.
- **Retain context-dependence**: keep only while it benefits Hestia.


This doctrine lets any machine-operator build **complementary, governed** tooling that plugs into Hestia’s ecosystem with minimal friction and maximum safety.

```yaml
TOKEN_BLOCK:
    accepted:
        - TOML_FIRST_DOCTRINE_OK
        - DYNAMIC_PATH_RESOLUTION_OK
        - DRY_RUN_APPLY_MODEL_OK
        - GOVERNED_WRITE_OK
        - CANONICAL_REPORT_LEDGER_OK
    requires:
        - ADR_SCHEMA_V1
        - ADR_0024_PATH_COMPLIANCE
        - ADR_0015_NO_SYMLINKS
    drift:
        - DRIFT: hard_coded_path
        - DRIFT: missing_toml_block
        - DRIFT: missing_report_or_ledger
        - DRIFT: non_atomic_write
        - DRIFT: missing_dry_run_apply
```

