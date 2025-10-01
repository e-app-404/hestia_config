## 🧠 CONTEXT SEED FOR GPT SESSION

You are resuming the HESTIA rebuild project, focused on reconstructing a consistent, semantically rich `omega_room_registry.json` based on prior mappings and a post-purge canonical `omega_device_registry`.

### PRIMARY INPUTS
- `omega_device_registry.cleaned.v2.json` ← canonical post-remediation device registry (source of truth)
- `pre-reboot_registry/omega_room_registry.json` ← layout and room-level entity groupings before the system reboot
- `pre-reboot_registry/alpha_sensor_registry.json` and `alpha_light_registry.json` ← entity role and tier mappings

### OBJECTIVE
Rehydrate a fresh `omega_room_registry.relinked.json` that:
- Retains the **room structure and room → roles map** from the pre-reboot registry.
- Resolves all entity references (sensors, lights, etc.) to current canonical `entity_id`s in `omega_device_registry.cleaned.v2.json`
- Uses **semantic fingerprinting, fuzzy name matching, and role inference** to remap old entries.
- Identifies and flags **low-confidence**, **missing**, or **obsolete mappings** for user review.

### OPTIONAL SUPPORT FILES
- `attribute_purge_remediation.v2.log.json` ← for trace verification
- `device_groups.json` ← can aid with indirect mappings
- `2025_06_09-HESTIA-REBUIILD/.../sensor_class_matrix.yaml` ← for functional tier evaluation

---

### ✅ RECOMMENDED STARTING STEPS FOR GPT

1. Load room layouts and entity groupings from `pre-reboot_registry/omega_room_registry.json`
2. Extract valid `entity_id`s from `omega_device_registry.cleaned.v2.json`, bucketed by area/domain.
3. Map pre-reboot entity references to cleaned IDs using:
   - name similarity (e.g., Levenshtein distance on snake_case names)
   - matching area/room
   - matching device class or domain
4. Flag entries where:
   - multiple candidates exist (ambiguous)
   - no suitable match exists (missing)
5. Emit:
   - `omega_room_registry.relinked.json` ← canonical rebuild
   - `relinking_trace.log.json` ← matching method + confidence per mapped entry
