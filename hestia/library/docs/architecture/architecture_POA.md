# Architecture POA for Hestia Metadata Schema

## 0) Setup & guardrails

* **Repo root**: treat `/config` as the root. Focus on `packages/`, `integrations/`, `templates/`, `*.yaml`.
* **Primary schema file**: `metadata_attributes.yaml` (a.k.a. “HESTIA Sensor Metadata Schema”).
* **Only touch** the schema file and generated reports/scripts unless instructed below.
* Prefer **non-destructive PRs**: add/change via new commits; don’t rewrite history.

---

## 1) Sweep the repo and **surface patterns not in the schema**

### 1.1 Inventory all entities + metadata attributes

* Parse every YAML under `/config` (ignore `/config/.storage`).
* Collect all entities (especially **template sensors/binary\_sensors**) and aggregate **attributes keys** actually used per entity:

  * Known keys: `module`, `role`, `type`, `tier`, `subsystem`, `canonical_id`, `file`, `upstream_sources`, `downstream_consumers`, `aggregation_strategy`, `source_count`, `version`, `created`, `last_updated`, `description`, `domain`, `area_id`, `subarea_id`, `container_id`, `data_quality`.
  * Also collect **HA-native** hints that should be schema fields but may currently live outside metadata: `unit_of_measurement`, `device_class`, `state_class`, `icon`, `entity_category`, `precision`, `availability_template`.
* Emit a **frequency report**:

  * Keys used that **don’t exist** in the schema (candidates for addition).
  * Keys defined in schema but **unused** (candidates for removal or demotion).
  * Value sets for enums (`module`, `role`, `tier`, `subsystem`, `type`), including **unknowns** or **misspellings**.

> Deliverable: `reports/metadata_field_usage.json` and `reports/enum_values_summary.md`.

### 1.2 Spot anti-patterns & inconsistencies

* Find attributes where a **list is stored as a string** (e.g., `'[ "sensor.a", "sensor.b" ]'`).
* Find `upstream_sources`/`downstream_consumers` that are **not lists**.
* Find **timestamps** (`created`, `last_updated`) not ISO-8601 or missing.
* Find **numeric sensors** (`state_class: measurement` or `total`, `total_increasing`) **missing `unit_of_measurement`**.
* Find `subsystem` values present in files that are **not in the schema enum**.
* Find **trailing commas** in enum arrays in the schema (JSON-schema tools hate them).

> Deliverable: `reports/metadata_inconsistencies.md` with file\:line pointers.

---

## 2) Enrich & harden the schema (apply my recs)

### 2.1 Fix enum mismatches

* **Add** missing subsystems mentioned in definitions to `subsystem.enum`: `chronos`, `perseus`, `hypnos`.
* Or, if those are accidental, **remove** their definitions. (Prefer **add**—they’re useful.)
* Normalize/remove **trailing commas** in all `enum` arrays.

### 2.2 Add new fields that make the schema more practical

Add these **as first-class properties** with definitions:

```yaml
data_quality:
  definition: >
    Qualitative assessment of data fidelity and provenance.
  enum: [runtime_observed, validated, simulated, deprecated]
  required: false

privacy_level:
  definition: >
    Sensitivity classification for this entity's data.
  enum: [public, internal, private, restricted]
  required: false

retention_policy:
  definition: >
    Suggested days to retain history (hint to Recorder/Influx governance).
  type: integer
  required: false

unit_of_measurement:
  definition: >
    Unit for numeric sensors; required when state_class indicates numeric stats.
  type: string
  required: false

validation_status:
  definition: >
    Current metadata validation state for CI pipelines.
  enum: [valid, pending_review, needs_fix, deprecated]
  required: false
```

### 2.3 Tighten types & formats

* For **dates**, keep `type: string` and add `format: date` (or `date-time` where you store timestamps).
* For `upstream_sources` & `downstream_consumers`, **enforce list** (YAML list). Allow JSON only as **serialization detail in attributes**, not in source YAML. Clarify this in `usage`.
* Consider **ASCII-safe machine key**:

  * Keep `canonical_id` human-friendly (UTF‑8 allowed).
  * Introduce optional `canonical_key` (ASCII only, pattern `^[a-z0-9_]+$`) for tooling that chokes on Greek letters.

### 2.4 Optional: add a **role taxonomy grouping**

* Group `role` enums into buckets in the docs (transformers, controllers, aggregators) to make selection easier. No validator impact—just docs.

---

## 3) Generate a **machine‑readable JSON Schema** + validator

### 3.1 JSON Schema (Draft 2020‑12)

* Generate `schema/metadata.schema.json` mirroring your YAML spec:

  * Define properties, `type`, `enum`, `format`, and `required` keys (`canonical_id`, `file`, `area_id`).
  * For enums: `module`, `role`, `type`, `tier`, `subsystem`.
  * Add **conditional**: if `state_class` ∈ {`measurement`, `total`, `total_increasing`} then `unit_of_measurement` is **required**.
  * Add **pattern** for `area_id`/`subarea_id`/`container_id` if you have canonical naming rules (e.g., `^[a-z0-9_]+$`).

### 3.2 Validator script

Create `tools/validate_metadata.py`:

* Walk `/config` YAMLs, extract **template entities** and read `attributes` block.
* Validate **per-entity metadata** against `schema/metadata.schema.json`.
* Check extras:

  * Ensure lists are real lists (coerce JSON strings to lists but warn).
  * Ensure ISO dates for `created`/`last_updated`.
  * Ensure `unit_of_measurement` exists for numeric `state_class`.
* Print **actionable report** and **non‑zero exit** on errors (for CI).

> Deliverables:
>
> * `schema/metadata.schema.json`
> * `tools/validate_metadata.py`
> * `reports/validation_results.json`

---

## 4) Auto‑fixers (limited, safe transforms)

Create `tools/autofix_metadata.py` to propose or apply **safe** changes:

* Convert JSON‑stringified lists → real YAML lists for `upstream_sources` / `downstream_consumers`.
* Insert missing `created`/`last_updated` (use file git history; fallback to current date; mark `validation_status: pending_review`).
* Add missing `unit_of_measurement` for obvious cases when you can infer from `device_class` (e.g., `temperature` → `°C`/`°F` **don’t guess units** unless a default is codified in repo).
* Remove trailing commas in local enum arrays if present anywhere.

Run autofix in “**dry‑run**” by default; support `--apply` flag.

> Deliverable: PR with per-file diffs when `--apply` is used.

---

## 5) Docs generation

Generate `docs/metadata_catalog.md`:

* One section per module/subsystem with a table:

  * `entity_id`, `canonical_id`, `module`, `role`, `type`, `tier`, `subsystem`, `area_id`, `unit`, `created`, `last_updated`, `validation_status`.
* Include counts + charts (optional) summarizing usage of roles/tier/subsystems.

> Deliverable: `docs/metadata_catalog.md` (update in PR).

---

## 6) CI & local ergonomics

* Add **pre‑commit** hooks:

  * `yamllint` (respect your style)
  * `tools/validate_metadata.py`
* Add **GitHub Action** `ci/metadata-validate.yml`:

  * On PRs touching `*.yaml`, run the validator and fail if errors.
  * Upload `reports/validation_results.json` as artifact.

---

## 7) Concrete prompts Copilot can act on

Paste these into Copilot Chat in your repo:

**A. Build the metadata inventory report**

> “Scan /config recursively for YAML. Extract all template sensor/binary\_sensor `attributes` blocks. Build a list of all metadata keys used and their frequency. Also gather the value sets for module/role/tier/subsystem/type. Save as `reports/metadata_field_usage.json` and `reports/enum_values_summary.md`.”

**B. Find inconsistencies & anti‑patterns**

> “Create `reports/metadata_inconsistencies.md` listing: attributes where lists are strings, missing ISO dates in created/last\_updated, numeric sensors missing unit\_of\_measurement when state\_class is numeric, and any subsystem values not in the schema enum. Include file and line pointers.”

**C. Generate JSON Schema & validator**

> “Create `schema/metadata.schema.json` (Draft 2020‑12) based on metadata\_attributes.yaml, including new fields: data\_quality, privacy\_level, retention\_policy, unit\_of\_measurement, validation\_status. Then write `tools/validate_metadata.py` to validate all entities’ metadata against it and produce `reports/validation_results.json`. Exit non‑zero on errors.”

**D. Write the autofixer**

> “Create `tools/autofix_metadata.py` that converts JSON‑string lists into YAML lists for upstream\_sources/downstream\_consumers, inserts missing ISO dates (using git history where possible), adds validation\_status: pending\_review for new/changed metadata, and removes trailing commas in enum arrays. Default dry‑run; support `--apply`.”

**E. Docs**

> “Generate `docs/metadata_catalog.md` with a table of all entities and their key metadata, grouped by module and subsystem, with counts of role/tier usage.”

**F. CI**

> “Add a GitHub Action workflow `/.github/workflows/metadata-validate.yml` that runs `tools/validate_metadata.py` on PRs and pushes `reports/validation_results.json` as an artifact. Add a pre‑commit hook to run the validator locally.”

---

## 8) Policy decisions Copilot should encode

* **Enums**: Update `subsystem.enum` to include `chronos`, `perseus`, `hypnos` (or remove their definitions—**prefer include**).
* **Dates**: Enforce ISO (`YYYY-MM-DD` for dates; `YYYY-MM-DDTHH:MM:SS±HH:MM` for date-time).
* **Lists**: Enforce YAML lists in source files; JSON lists only when serializing into HA attributes.
* **IDs**: Keep `canonical_id` as-is (UTF‑8 OK). Add optional `canonical_key` with ASCII pattern if needed by tooling.
* **Numeric sensors**: If `state_class` is numeric, **require** `unit_of_measurement`. Don’t guess units unless clearly codified elsewhere.
* **Trailing commas**: Remove in schema enums.

---

## 9) Acceptance criteria (what “done” looks like)

* `reports/metadata_field_usage.json` & `reports/enum_values_summary.md` exist and look sane.
* `reports/metadata_inconsistencies.md` points to real issues (or is empty).
* `schema/metadata.schema.json` validates your existing metadata (modulo expected failures that the autofixer can resolve).
* `tools/validate_metadata.py` returns **0** after autofixes are applied.
* `docs/metadata_catalog.md` is generated and readable.
* CI workflow passes on a fresh PR touching YAML.
* Schema file (`metadata_attributes.yaml`) updated with:

  * enum fix for `subsystem`
  * new fields (`data_quality`, `privacy_level`, `retention_policy`, `unit_of_measurement`, `validation_status`)
  * clarified types (`format: date` / `date-time`)
  * clarified list handling

---
