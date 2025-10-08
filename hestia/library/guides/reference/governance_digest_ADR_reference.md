---
title: "Governance Digest — ADR & Reference Walkthrough"
slug: governance_digest_adr_reference
date: 2025-10-08
authors: "Strategos GPT"
tags: ["home-assistant", "ops", "governance", "adr", "reference", "templates", "sql", "mqtt", "valetudo", "motion-lights", "adaptive-lighting"]
original_date: "2025-10-08"
last_updated: "2025-10-08"
---

# Governance Digest — ADR & Reference Walkthrough

**Scope:** packages · YAML · SQL sensors · templates · database interaction · MQTT commands · Valetudo · motion lights · adaptive lighting
**Date:** 2025‑10‑08 (Europe/London)
**Source Sets:** `ADR/`, `reference/`, `ha_implementation/` (unpacked from user tarballs)

---

## 0) High‑level Guardrails (from ADRs + workspace patterns)

* **Single source of truth for recorder/database config** — maintain **one canonical** `recorder:` block; CI should block duplicates.
* **Tiered architecture enforcement** — automations consume **β-tier composites**; **no extra abstraction above β** for motion→light flows.
* **Blueprint‑first motion lighting** — core logic via `library/blueprints/sensor-light*.yaml`; per‑room specifics in `packages/motion_lights/*`.
* **YAML determinism** — normalize Jinja; prefer safe conversions and explicit checks to avoid `unknown/unavailable` pitfalls.
* **Extensions & includes** — Only `.yaml` (not `.yml`); strict include directives; structure under `/config/hestia/*` and `/config/packages/*` per role.

---

## 1) YAML & Packages

### 1.1 Include/directive governance

* Supported: `!include`, `!include_dir_list`, `!include_dir_named`, `!include_dir_merge_list`, `!include_dir_merge_named`, **`packages: !include_dir_named`**.
* Only **`.yaml`** files; reject `.yml`.
* Paths are **relative to `/config/`**; validate shape per directive (list vs mapping).
* Lists must be **alphabetically ordered**; for mappings, **last‑key‑wins**.

### 1.2 Repository layout cues found in ADRs

* Keep domain logic grouped: `/config/packages/` for deployable feature bundles; `/config/hestia/` for system meta (signal emitters, class matrices, logic indexes).
* Example structure hints (from strategy files): `packages/motion_lights/*.yaml`, `packages/adaptive_lighting/*.yaml`, `templates/`, `devices/valetudo.yaml`, `devices/motion.yaml`.

**Actions:**

* Enforce a repo check that fails `.yml` and unordered lists; verify `packages: !include_dir_named packages/` at the root.

---

## 2) Templates (Jinja) — Normalization Rules (ADR‑0002)

**Decision:** Standardize Jinja patterns used in Home Assistant to reduce runtime errors and drift.

**Key patterns (selected):**

* **Datetime parsing & comparison:**

  * Replace direct `now()` vs. string comparisons with `as_datetime()` guard rails and truthiness checks.
* **State safety:**

  * Always guard against `unknown`/`unavailable`/empty string; avoid direct arithmetic on raw `states()`.
* **Type‑safe math:**

  * Coerce via `|int`, `|float` with defaults; never assume numeric.

**Implication:** Template sensors/conditions in blueprints and packages must apply these normalized forms.

---

## 3) SQL Sensors & Database Interaction

### 3.1 Recorder & DB policy (ADR‑0014)

* **Single canonical `recorder:` config** in the repo.
* **Short retention window** (e.g., 7 days) traded for stability.
* CI must **block** duplicate `recorder:` sections and non‑idempotent content.

### 3.2 SQL sensors usage notes (workspace docs)

* Use SQL sensors primarily against the **Recorder** DB; external DBs allowed but must document connection & impact.
* Favor **read‑only, indexed** queries; avoid high‑frequency polling on large tables.
* Prefer **computed attributes** via Jinja where SQL would otherwise fan‑out joins.

**Actions:**

* Add lints for: (a) duplicate `recorder:` blocks, (b) heavy `SELECT *` without `LIMIT`, (c) sub‑minute scan intervals.

---

## 4) MQTT Commands & Discovery

### 4.1 Discovery governance (reference analysis)

* Maintain a **playbook** for MQTT discovery covering device‑level vs per‑component discovery.
* When feasible, prefer **device‑based discovery payloads** (single publish) over multi‑component fragments.

### 4.2 Command publishing

* Use `mqtt.publish` for imperative commands; document **`command_topic`** and **`state_topic`** contracts for each device domain.
* Ensure retained flags and QoS are chosen per device requirements; avoid retained **commands** unless the device demands it.

**Actions:**

* Keep a discovery audit doc current; validate that published discovery topics match entity naming conventions.

---

## 5) Valetudo (Vacuum) Integration

* Connection path: **Valetudo → Mosquitto (MQTT) → HA (MQTT discovery)**.
* Broker: **Mosquitto** recommended (HAOS add‑on or external). Point both HA and Valetudo to the **same broker**.
* Prefer Valetudo’s **autodiscovery** where available; otherwise define component topics explicitly.

**Actions:**

* Validate that `devices/valetudo.yaml` or equivalent maps to the broker in use; include a minimal command/state topic checklist.

---

## 6) Motion Lights & Adaptive Lighting — Package Policy (reference blueprint + ADR‑0021)

### 6.1 Motion/Presence governance (ADR‑0021)

* **Presence must not gate activation** in this household profile; it may **enhance** timeouts or scenes.
* **Single abstraction layer:** Automations **consume β‑tier composites** (motion/occupancy/illuminance) and target **η‑tier** light groups. **No extra layer above β**.

### 6.2 Adaptive Lighting interplay (reference package)

* **Required blueprint inputs:**

  * `motion_sensors` (≥1), `target_lights` (η‑tier groups), `timeout_seconds`, `trigger_entities`, `trigger_on_state`, `trigger_off_state`, `linked_entities`.
* **AL coexistence rule:** When Adaptive Lighting is enabled for a room, the **motion package does not set brightness/CT**; AL holds those concerns.
* **Room profiles (var integration):** Per‑room variables drive AL policy (`al_enabled`, `sleep`, `default_brightness_pct`, `night_*` settings, `presence_boost_timeout`).
* **AL switches:** Use one AL switch per room (derived from `name:`), e.g., `switch.adaptive_lighting_bedroom`.
* **Operational flags:** `only_once: true`, `take_over_control: true`, `initial_transition: 0.3` are recommended defaults per room.

**Actions:**

* Add room‑profile validators; test that motion packages don’t write brightness/CT when AL is active.
* Provide per‑room AL + motion audit (templated) to visualize policy and recent triggers.

---

## 7) Concrete Checks to Automate (short list)

1. **File hygiene**: reject `.yml`; enforce alpha‑ordered lists; verify include shapes; confirm `packages: !include_dir_named packages/` at root.
2. **Recorder**: assert single `recorder:`; retention ≤ 7d; CI block on duplicates.
3. **SQL sensors**: warn on `SELECT *`, missing `LIMIT`, polling < 60s, joins without indexes.
4. **MQTT**: validate discovery payload completeness; warn on retained commands; flag command/state topics missing in device manifests.
5. **Motion/AL**: ensure presence doesn’t hard‑gate; audit that motion packages omit brightness/CT when AL enabled.

---

## 8) Evidence Pointers (paths)

* ADRs: `ADR/ADR-0002-jinja-patterns.md`, `ADR/ADR-0014-oom-and-recorder-policy.md`, `ADR/ADR-0021-motion-occupancy-presence-signals.md`, `ADR/architecture_POA.md`, `ADR/hestia_structure.md`.
* References: `reference/README_package_adaptive_motion_lights.md`, `reference/mqtt_discovery_comprehensive_analysis.md`.
* Implementation notes: `ha_implementation/integration.sql.md`, `ha_implementation/integration.sensor-sql.md`, `ha_implementation/integration.recorder.md`, `ha_implementation/integration.valetudo.md`.

---

## 9) Open Questions / Follow‑ups

* Confirm actual **retention days** used in your active `recorder:`.
* Inventory current **SQL sensors** and mark heavy queries.
* Broker check: verify **one broker URL** across HA and Valetudo.
* Run an **AL/motion audit** to validate coexistence rules room‑by‑room.
