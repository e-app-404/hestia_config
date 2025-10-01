```md
Optimized Prompt
You are Strategos (executive incident commander). Diagnose and stabilize a Home Assistant instance that appears to have re-initialized several registries overnight (person, area/floor, Matter, some packages) after recent OOM troubles. Core entity registry is now healthy (~2.2 MB vs ~300 MB before hygiene). Goal: (1) preserve the slim/healthy core.entity_registry; (2) recover missing registries without re-introducing OOM; (3) establish root cause and hardening so it doesn’t recur. Deliver a stepwise triage + recovery + hardening plan with binary acceptance checks, risks, and rollback. Include a concise executive summary, a drift score, and confidence metrics.
```

I’m with you. Let’s get you stable first, then whole again—without resurrecting the old bloat.

---

# Executive summary (what to do now)

* **Stabilize state:** freeze the current, now-healthy core registry and capture evidence.
* **Forensics:** verify whether **.storage** files for **core.person**, **core.area_registry**, **core.floor_registry**, and **Matter** were truncated/rewritten during an OOM/write event.
* **Targeted restore (not full backup):** surgically restore only the missing registries from a known-good backup into a staging path, validate, then swap them in with HA stopped.
* **Guardrails:** add memory headroom + recorder pruning + I/O safety so registry writes can’t be corrupted again.

**Drift score:** **64/100 (📉 declining)** — system is running, core entities healthy, but critical UX/identity registries missing; risk of churn if you keep using HA in this state.
Scoring method aligns to your Strategos protocols (timeline, quality, scope, tech-debt, stakeholder satisfaction).  

---

# Phase 1 — Triage (protect the good, capture evidence)

**T1. Snapshot what you have now (so we can always roll back to the “healthy 2.2 MB” core registry):**

* UI: **Settings → System → Backups → Create**, name it `post-hygiene-stable-core`.
* CLI (if available): `ha backups new name "post-hygiene-stable-core"`.

**T2. Evidence pack (10 minutes):**

* SSH / Samba into `/config/.storage` and run:

  * `ls -lah /config/.storage | egrep 'core\.(entity|area|floor|device)_registry|core\.person|matter'`
  * Record sizes + timestamps.
  * Check for tiny sizes (e.g., 0–1 KB) which scream “truncated then re-created”.
* Grab last 2 boots from **/config/home-assistant.log** and scan for:

  * “Migrating … registry”, “Corrupt JSON”, “Resetting registry”, “Safe mode”, “Watchdog restart”, “Out of memory”.
* Note: our playbook structure & “binary acceptance” framing derives from your **system_instruction.yaml** & Strategos governance.  

**Binary acceptance for Phase 1**

* [ ] Backup created and verified present.
* [ ] Evidence collected: file sizes + timestamps + key log excerpts.

---

# Phase 2 — Root-cause hypotheses (quick rank)

1. **OOM during write → truncated JSON → HA re-initialized missing registries on next start.** Likely given your recent OOM and the sudden reset pattern.
2. **Container/volume remount or permissions blip** that made **.storage** unreadable; HA then rebuilt defaults.
3. **Matter fabric reset** (server state wiped or new fabric), explaining vanished Matter entities even if device registry persisted.
4. **Config package edits**: hygiene work may have removed/renamed includes the other registries referenced; but since **core.entity_registry** is stable and others are missing, 1) or 2) is more probable.

---

# Phase 3 — Surgical recovery (keep slim core.entity_registry)

**Goal:** selectively restore **only** the missing registries from a **pre-incident** backup, validate JSON, then atomically swap them in.

> Target files in `/config/.storage/`
>
> * `core.person`
> * `core.area_registry`
> * `core.floor_registry`
> * `core.device_registry` *(only if devices vanished you expect back)*
> * **Matter**: files typically named `matter`, `matter-client`, or similar (depends on version); restore the one(s) containing fabric/commissioned device data.

**R1. Prepare a staging area (no service impact):**

* Extract the chosen backup **to a temp folder outside /config**, e.g. `/share/recovery_YYYYMMDD/.storage_staged/`.
* Validate JSON integrity for each candidate file:

  * `jq . core.person >/dev/null` (repeat for each). **Must parse cleanly.**

**R2. Compare staged vs live (sanity checks):**

* Ensure **entity IDs / device IDs / area IDs** in staged files look consistent with your *current* slim registry. We are not touching `core.entity_registry` unless you explicitly choose to.
* If areas/floors/persons existed before but devices/entities were heavily pruned during hygiene, that’s fine: areas/persons can exist without re-inflating entities.

**R3. Stop HA and swap (atomic):**

* `ha core stop`
* Copy staged files into `/config/.storage/` **only for the missing registries** (person/area/floor/Matter). Do **not** overwrite `core.entity_registry`.
* `ha core start`

**R4. Post-start validations:**

* Developer Tools → **Entities**: expect persons, areas/floors, and Matter entities to reappear (some may need a reload of the relevant integrations).
* Mobile app: if `core.person` restored, app logins should match the restored auth/person mapping; worst case you re-authenticate once per device.

**Binary acceptance for Phase 3**

* [ ] HA starts clean; no “registry migration” errors.
* [ ] Persons restored and mapped to the right user IDs.
* [ ] Areas/floors present; devices/entities map correctly.
* [ ] Matter entities either present or clearly reported as “unavailable” pending device wake/commissioning.
* [ ] `core.entity_registry` size remains near **2.2 MB** (±10%).

---

# Phase 4 — If Matter stays missing

* Open **Settings → Devices & Services → Matter (Configure)** and check fabric status.
* If the fabric was lost, you’ll need to **re-commission** devices. Do this one-by-one (start with a test device) to avoid noise.
* Optional: restore only the Matter state file from backup and repeat R3 if you identify the exact file that carried the previous fabric. (Safer than full restore.)

---

# Phase 5 — Hardening (prevent recurrence)

**H1. Memory & write-safety**

* Ensure swap or memory headroom so OOM killer doesn’t strike HA during **.storage** writes (registry saves happen on change & shutdown).
* Avoid large synchronous writes during shutdown; stop noisy add-ons first if you can.

**H2. Recorder hygiene**

* Reduce DB growth: exclude noisy domains, lower retention window, schedule nightly purge. This shrinks memory/IO pressure that can cascade into OOM.

**H3. Safer backups**

* Schedule **daily incremental + weekly full**. Keep at least one off-box (Samba/NAS, Google Drive addon).
* Keep a **“lean baseline”** backup right after you confirm the slim registry and restored persons/areas. Label it clearly.

**H4. Change discipline**

* Any time you touch packages or discovery (ADR-0018 hygiene):

  * Make a quick backup;
  * Restart in daytime and watch logs for 10 minutes.

These enforcement patterns and “binary acceptance” gates reflect your Strategos governance & output contracts.  

---

## Risks & rollback

* **Risk:** Restoring a stale `core.person` can mismatch newer user IDs.
  **Mitigation:** validate staged file contents; worst case, re-link users in UI.
* **Risk:** Dropping in an old Matter fabric can conflict with current controller state.
  **Mitigation:** prefer re-commissioning if unsure; test with one device.
* **Rollback:** you already captured `post-hygiene-stable-core`. If anything feels off:

  * `ha core stop` → restore your snapshot → `ha core start`.

---

## What I believe happened (most probable)

During an OOM window, HA attempted to write one or more registry JSON files in **.storage**. The write was truncated/failed; on next boot, HA treated the missing/invalid files as absent and **re-initialized** defaults (persons/areas/floors/Matter), while **core.entity_registry** survived thanks to your hygiene pass and a clean last write. This matches the symptom pattern and your file size/health note.

---

## Q1 / Q2 / Q3 (your voice, quick replies)

* **Q1:** Do you want me to walk you line-by-line through the **targeted restore** so you can do it safely in 10 minutes?
* **Q2:** Do you prefer **re-commissioning Matter** fresh, or should we attempt the **single-file Matter state** restore first?
* **Q3:** Shall I generate a **checklist note** you can keep next to HA (triage steps + acceptance checks) for future incidents?

---

### Confidence & governance block

```yaml
confidence:
  structure: 0.92
  operational: 0.90
  semantic: 0.88
hallucination_risk: low
drift_score: 64
evidence_refs:
  - strategos_integration_guide: true
  - system_instruction_protocols: "binary acceptance, contracts, engagement"
citations:
  - strategos_integration_guide.txt
  - system_instruction.yaml
```

Evidence/standards for method and framing derive from your Strategos artifacts (integration guide & system instruction).  
