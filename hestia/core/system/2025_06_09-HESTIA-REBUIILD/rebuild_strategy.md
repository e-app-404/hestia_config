# HESTIA Rebuild Strategy (rebuildstrategy.md)

## 🧭 **Why HESTIA**

HESTIA is more than a smart home initiative—it's a testbed for a new class of autonomous, contract-driven AI systems. Its architectural rigor, tier discipline, and declarative tool orchestration provide a rare example of AI augmentation executed with control, transparency, and semantic intent. The reboot honors this foundation by elevating it into a fully introspective, production-ready platform.

## 🧭 Project overview

A phased, modular reboot of the HESTIA Home Assistant configuration and runtime system.
This rebuild emphasizes logic clarity, semantic role assignment, and minimal carry-over of unstructured legacy logic.

## 🔧 Objective

Reboot the HESTIA Home Assistant environment with precision, eliminating accumulated cruft and restoring an operational, modular configuration. This strategy orchestrates the transition from the current chaotic state to a clean, logic-aligned runtime setup.

With this reboot, we want to align all efforts towards transforming the HESTIA Home Assistant ecosystem into a **production-hardened, maintainable, and extensible** smart home platform while preserving critical automations and minimizing service interruption during the transition. This transformation will reinforce HESTIA as a provable model of disciplined, self-documenting AI-assisted infrastructure.

### 📊 **Risk-Adjusted Phase Structure**

| Phase    | Purpose                              | Duration | Risk Level  | Rollback Strategy   |
| -------- | ------------------------------------ | -------- | ----------- | ------------------- |
| **P0**   | **System Archeology & Preservation** | 2-3 days | 🟡 Medium   | N/A (Read-only)     |
| **P0.5** | **Production Backup & Safety Net**   | 0.5 days | 🟢 Low      | Full system restore |
| **P1**   | **Controlled Deconstruction**        | 2-3 days | 🟠 High     | Snapshot rollback   |
| **P2**   | **Foundation Rebuild**               | 3-4 days | 🔴 Critical | Staged deployment   |
| **P3**   | **Entity Logic Migration**           | 4-6 days | 🟠 High     | Per-domain rollback |
| **P4**   | **Integration & Validation**         | 2-3 days | 🟡 Medium   | Feature flagging    |
| **P4.5** | **CI-Driven Pre-Hardening Check**    | 1 day    | 🟢 Low      | Phase re-entry      |
| **P5**   | **Production Hardening**             | 2-3 days | 🟢 Low      | Gradual rollout     |

### 🔍 **Critical System Assessment Findings**

#### **Complexity Factors Identified:**

* **Tiered Architecture**: Complex α→ζ sensor hierarchy requiring careful migration
* **Subsystem Stratification**: Tools (Hephaestus, Mnemosyne, Olympus, Config Manager) and knowledge modules (Aether, Theia, Hermes) form layered abstractions
* **Motion/Presence Pipeline**: 8+ room presence detection with decay logic and inference layers
* **Registry Dependencies**: Heavy reliance on `omega_room_registry.json` and `alpha_sensor_registry.csv`
* **Template Macros**: Extensive Jinja2 macro library (`template.library.jinja`) with cross-dependencies
* **Automation Complexity**: 35+ automations with interdependent triggers

#### **Preservation Requirements:**

* ✅ **Critical**: Motion/occupancy detection, lighting automations, climate control, CLI tools, macro library
* ⚠️ **Important**: Presence inference, room registry, sensor abstraction layers
* 📦 **Archive**: Legacy validation chains

### 🗂️ **Artifact Index & Configuration Inventory**

| Artifact Name                          | Purpose                                  | Phase | Owner/Subsystem | Schema/Contract        | ✅ Validation Hook?         | ⚠️ Test Strategy?           | 🔍 Namespace Clarity          | 🛠️ Recommendation                                |
| -------------------------------------- | ---------------------------------------- | ----- | --------------- | ---------------------- |  -------------------------- | --------------------------- | ----------------------------- |-------------------------------------------------- |
| `canonical_index.yaml`                 | Classify preservation-critical assets    | P0    | Hermes          | Declarative mapping    | Partial (manual)            | ❌ None defined             | ✅ Clear (Hermes domain)      | Define structural schema (`canonical.schema.yaml`)|
| `entity_map.json`                      | Tier-to-owner mappings of entities       | P0-P3 | Olympus         | Governance/validation  | ✅ Enforced in Olympus      | ✅ Tier+Owner mapped        | ✅ Aether-aligned            | Add audit logs when tier conflicts arise           |
| `macro_coverage_report.json`           | Template macro dependency report         | P2    | Hephaestus      | Coverage/test planning | ❌ Missing generator        | ❌ No test plan yet         | ✅ Scoped under Hephaestus     | Build macro audit tool with `jinja-lint` base    |
| `main.conf`                            | Config base for runtime tool behavior    | P2-P5 | Config Manager  | Runtime contract       | ✅ Runtime-loaded           | ⚠️ Schema partially implied | ⚠️ Ambiguous overrides        | Enforce schema with `foundation.schema.conf`      |
| `foundation.schema.conf`               | Schema for base configuration            | P1    | Olympus         | Validation             | ✅ Central validator        | ✅ Anchors CLI              | ✅ Clearly namespaced          | No action needed                                 |
| `hardening_readiness_report.yaml`      | Pre-P5 CI evaluation result              | P4.5  | Olympus         | Gatekeeping            | ❌ Not yet defined          | ❌ CI triggers TBD           | ⚠️ Cross-subsystem (Olympus?) | Define emission logic, CI stage ID anchors       |
| `omega_room_registry.json`             | Room → motion sensor registry            | P0-P3 | Aether          | Sensor mapping         | ✅ Used in entity pipelines | ⚠️ Partial test coverage    | ✅ Scoped under Theia          | Add dependency graph tests                       |
| `alpha_sensor_registry.csv`            | Cross-sensor abstraction registry        | P0-P3 | Aether          | Mapping/QA logic       | ⚠️ Used but not validated  | ❌ No QA on schema           | ⚠️ CSV format = fragile       | Convert to JSON or YAML for typed validation      |
| `template.library.jinja`               | Reusable Jinja2 macro base               | All   | Hephaestus      | Templating             | ✅ Runtime tested           | ⚠️ No macro test suite      | ✅ Hephaestus owned            | Add macro lint + test harness per usage tier     |
| `config_files.py`, `config_runtime.py` | Load and override config states          | P1-P5 | Config Manager  | Modular I/O            | ✅ CLI-tested               | ⚠️ Schema diffing undefined | ✅ Namespaced cleanly          | Add `--schema-diff` and `--validate` CLI options |

---

### 💡 **Strategic Recommendations**

1. **Adopt Infrastructure-as-Code**: All configurations should be version controlled and deployable
2. **Implement Gradual Migration**: Use feature flags to enable new systems alongside legacy
3. **Create Living Documentation**: Promote self-updating documentation through toolchain telemetry and config state introspection
4. **Establish Change Management**: Formal process for future modifications
5. **Enforce Tier Contracts**: Gate entity migrations by tier identity and ownership via `entity_map.json`
6. **Integrate Schema-Locked Config Validation**: Prevent misconfig-driven runtime errors across phases
7. **Codify Subsystem Orchestration Contracts**: Define stable interfaces and output expectations between subsystems (e.g., Mnemosyne ↔ Olympus, Hephaestus ↔ Config Manager)
8. **Phase-Centric Semantic Logs**: Emit traceable logs tied to execution phase, enabling post hoc debugging and proof of correctness

## Reboot Activity Tracker

### 📋 Phase 0: Pre-Reset Validation Audit, Index, and Extraction (COMPLETE)

**Goal:** Exhaustive traversal and audit of the `/share` volume contents to build a validated knowledge graph and logic trace system prior to reset.

* [x] Audit `core/`, `meta/`, `work/` directories for preservation value
* [x] Parse all relevant `.tar.gz`, `.yaml`, and `.jinja` files
* [x] Compile `hestia_canonical_index.yaml` with role tagging and preservation intent
* [x] Finalize `handoff_scaffold` with validated runtime artifacts

#### Phase 0 Activity Details

* Full extraction and inspection of:

  * `core.entity_registry`
  * `core.device_registry`
  * `core.config_entries`
  * `config.custom_templates`
  * `hestia.tar.gz`, `meta_*.tar.gz`, `work_.tar.gz`

* Recursive parsing of all YAML, Markdown, and Jinja2 logic sources
* Generation of runtime signal emitters and class matrix
* Logic path mapping from templated macros and automations
* Canonical index buildout with fate-tagging

#### Phase 0 Artifacts Produced

* `hestia_canonical_index.yaml` (live content + metadata + utilization matrix)
* `signal_emitters.yaml`
* `sensor_class_matrix.yaml`
* `logic_path_index_v1.1.yaml`
* `hestia_reboot_strategy_contract.yaml`
* Parsed JSONs for core.* registries

### Key Insights

* Numerous orphaned or misconfigured sensors identified
* Key runtime macro templates found in `custom_templates/`
* `work/context/`, `core/gnos/`, and `work/tools/` contain operational value
* Redundant copies in `vault/` and stale logic in `design_principles.md` slated for archival
* Misclassification of artifact completeness detected and corrected for logic outputs

---

### 🔁 Phase 1: Environment Reset & Fresh Baseline Deployment

**Goal:** Establish a fresh Home Assistant deployment surface
**Method:** Reset Home Assistant environment, apply version-controlled scaffold, and restore minimal runtime architecture.

Tasks:

* [ ] Wipe current config volume (retain only GDrive/sync-neutral folders)
* [ ] Deploy latest Home Assistant stable version
* [ ] Mount `/share`, `/config`, `/media`, `/custom_templates`, `/vault` cleanly
* [ ] Activate minimal dev-only `configuration.yaml` with diagnostics enabled

#### Phase 1 Activity Details

* Wipe runtime config, deploy clean Home Assistant base
* Mount `/config` as Git-tracked workspace
* Inject from `handoff_scaffold:`

  * `init.yaml`
  * core.* registries
  * validated signal/class/logic maps
* Restore macro templates, bootstrap minimal automations

### 🧱 Phase 2: Core Bootstrap

**Goal:** Rehydrate runtime logic and reference configuration

Tasks:

* [ ] Inject `config/init.yaml` with references to:

  * `output/signal_emitters.yaml`
  * `output/sensor_class_matrix.yaml`
  * `output/logic_path_index.yaml`
* [ ] Load registries:

  * `core.entity_registry`
  * `core.device_registry`
  * `core.config_entries`
* [ ] Activate CLI and devtool environment (e.g., `cli_emit.py`, `runtime_fanout.yaml`)

### 🧠 Phase 3: System Role Assertion

**Goal:** Assert GPT behavior, schema validation, and prompt logic

Tasks:

* [ ] Inject `system_instruction_patch.yaml`
* [ ] Activate `persona/promachos.yaml` and load into runtime
* [ ] Validate prompt routing logic from `core/gnos`, `work/context`
* [ ] Confirm `gpt_playbook.md` and `tool_manifest.yaml` linkages

### 🌐 Phase 4: Integration Rehydration

**Goal:** Restore integrations in full operating logic

Tasks:

* [ ] Reconnect ESPHome, MQTT, Zigbee
* [ ] Validate devices via `device_registry`
* [ ] Use preserved entity IDs from `signal_emitters.yaml` to restore automation compatibility

### 📊 Phase 5: Runtime Diagnostic Assurance

**Goal:** Validate runtime correctness and signal propagation

Tasks:

* [ ] Run diagnostics on logic paths defined in `logic_path_index.yaml`
* [ ] Confirm emitter-template consistency
* [ ] Review CI hooks and format linters

### ✅ Exit Criteria

* All active automations mapped and operating
* Canonical runtime logic validated
* Signal emitters functionally tested
* GPT behavior fully loaded and responding to system cues
* Reboot strategy marked `complete`
