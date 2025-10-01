# 📐 HESTIA Sensor Audit Prompt Scaffold (Phase 1)

## 📌 Phase

`hestia_sensors_revisited_01 → phase_1_audit_index_classify_map`

## 🔁 Execution Mode

`audit → index → classify → map`

---

## 🗂️ Archive and File Discovery

**Extract and scan (in this order):**

1. `sensors.tar` — canonical YAML-defined sensors
2. `binary_sensors.tar` — binary_sensor blocks
3. `integrations.tar`, `automations.tar`, `core.tar` — secondary sensor sources
4. Skip `tools.tar` unless a clean version is present

Instruction:
Recursively parse all `.yaml` files. Record each file's `source_path`.

---

## 🧠 Sensor Parsing & Composition Rules

For each YAML list item inside any `sensor` or `binary_sensor` block:

- Treat the item as a candidate entity
- Parse keys at **top level** and inside `attributes:` if applicable
- Extract:

  - `name` (primary semantic anchor)
  - `entity_id` (explicit or inferred)
  - `unique_id` (explicit or inferred)
  - `domain` (default = `"sensor"`)
  - `platform` (default = `"template"` if missing but state/attributes present)
  - `template_ref`, `used_by`, `declared_attributes`, `lineage_trace`

---

### 🔍 Entity ID Derivation Heuristic

If `entity_id` is not declared but `name` is:

```python
entity_id = f"{domain}.{slugify(name)}"
```

Where `slugify()`:

- Converts to lowercase
- Replaces non-alphanumerics with `_`
- Normalizes Unicode (NFKD) and strips accents

---

### 🔐 Canonical ID Strategy

Canonical ID should be a stable, hash-derived fingerprint.
Prefer this fallback order:

1. Hash of `entity_id`
2. Hash of `unique_id`
3. Hash of `slugified(name + source_path)` if others are blank

Avoid empty string hashing — substitute entropy (e.g., file hash) to prevent `d41d8cd98f`.

---

### ✅ Validation Status Classification

```text
ok                 → entity_id and unique_id resolved
missing_id         → both fields blank after derivation
duplicate          → collision on entity_id or unique_id across sources
unresolved_template→ template_ref cannot be resolved
broken_ref         → used_by or attribute ref not defined anywhere
```

For every record, attach an embedded comment if the status is not `ok`:

```yaml
validation_hint: "entity_id inferred from name: 'Gamma-Tier Macro Library'"
```

---

### 🧬 Pattern + Tier Detection

- Parse `attributes.tier`, `attributes.role`, `attributes.macros`
- If macro fields are present, annotate:

  - `pattern_status: matches_macro_library_block`
  - `tier_annotation: <γ, μ, β>`

- These patterns will be matched against `DESIGN_PATTERNS.md` tier definitions

---

### 📄 Required Output Format

Emit a single YAML file: `phase_1_sensor_index.yaml`

```yaml
phase: phase_1_audit_index_classify_map
generated: <UTC timestamp>
summary:
  ok: <int>
  missing_id: <int>
  duplicate: <int>
  unresolved_template: <int>
  broken_ref: <int>

entities:
  - entity_id: sensor.gamma_tier_macro_library
    name: Gamma-Tier Macro Library
    unique_id: gamma_tier_macro_library
    canonical_id: <sha1 hash>
    domain: sensor
    platform: template
    validation_status: ok
    validation_hint: "entity_id inferred from name"
    source_file: sensors/gamma/gamma_tier_macro_library.yaml
    template_ref: []
    used_by: []
    declared_attributes: { ... }
    lineage_trace: []
    pattern_status: matches_macro_library_block
    tier_annotation: μ
```

**Do not crosslink `used_by` references in Phase 1.** This is deferred to Phase 2 (lineage and downstream impact analysis).

---

### 📬 Deliverables

1. Structured `phase_1_sensor_index.yaml`
2. Summary block with status counts
3. Per-entity validation_hint annotations where inference or assumptions were made

---
