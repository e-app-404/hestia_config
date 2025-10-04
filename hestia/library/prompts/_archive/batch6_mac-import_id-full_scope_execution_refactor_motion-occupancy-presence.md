Begin **full-scope execution** of motion, occupancy, and presence sensor refactoring using validated source artifacts and canonicalized directory structure under `/config/hestia`.

**Execution Mode:** `generate`
**Signoff Policy:** `auto_affirm_with_prompt`
**Directory Context:** Fully aligned to:
- `sensor: !include_dir_merge_named hestia/sensors/alpha`
- `template: !include_dir_merge_named hestia/inference`
- `binary_sensor: !include_dir_merge_named hestia/logic`

---

**Directives:**

1. **Do not pause or await confirmation.**
   - Proceed until:
     - All refactoring goals are completed
     - OR failure/oversight is fully documented in `tools/validation_tools/validator_log.json` with phase markers.

2. **Logging & Monitoring:**
   - Emit inline execution logs after every 3 files.
   - Track and append:
     - `confidence_metrics` block (structural, operational, semantic)
     - `hallucination_probability` (`p`) per file

3. **Auto-Recalibration Rules:**
   - If `confidence.structural < 0.85` OR remains `< 0.90` over 2 files:
     - Halt briefly to re-read the motion refactoring doctrine
     - Re-align execution stack with latest `motion_sensor_refactoring_POA_2025-06-05.md`

4. **Hallucination Threshold:**
   - `p < 0.10` is strictly enforced. Escalate violations to `validator_log.json`.

---

Upon completion, validate that the following files exist and are correctly placed:

- `sensors/alpha/motion.yaml`
- `inference/motion_inference.yaml`
- `inference/occupancy_inference.yaml`
- `logic/presence_logic.yaml`
- `logic/climate_zone.yaml`
- `logic/automation_triggers.yaml`
- `templates/template.library.jinja`

Trigger `configuration.yaml` stub export if post-placement success is confirmed.
