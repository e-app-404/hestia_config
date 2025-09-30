# Patch A — join_enricher.py (propagate area_id when present)

@@

- if area_id_present: log [JOIN-SKIP] and continue

+ if area_id_present:
- output["area_id"] = input["area_id"]
- output["_meta"]["inferred_fields"]["area_id"] = {
-     "join_origin": "core.entity_registry",
-     "join_confidence": 1.0,
-     "field_contract": "verbatim from entity_registry"
- }
- continue

# Rationale & expected results per transcript: entities with registry area_id must never end unresolved. filecite:turn35file17

# Patch B — area_floor_enricher.py (fix exemption logic)

@@

- if sensor_type in ["logic","template","virtual"]: area_id=None; annotate exemption; return

+ if sensor_type in ["logic","template","virtual"]:
- if entity.get("area_id"):
-     # preserve & annotate canonical source
-     meta.inferred_fields.area_id = {"join_origin":"core.entity_registry","join_confidence":1.0,"field_contract":"verbatim from entity_registry"}
- else:
-     entity["area_id"] = None
-     meta.inferred_fields.area_id = {"join_origin":"exemption","join_confidence":0.0,"field_contract":"area_id exempted for logic/template/virtual","exemption_reason":"not applicable"}

# Only exempt if missing everywhere. filecite:turn35file11

# Patch C — tier from unique_id/entity_id token

@@

- tier = tier_enricher.infer(...)

+ if unique_id.endswith(("_alpha","_beta","_gamma","_delta","_epsilon","_zeta")):
- tier = parse_suffix(unique_id)
- meta.inferred_fields.tier = {"join_origin":"unique_id tier token","join_confidence":1.0,"field_contract":"direct token"}
- else:
- tier = tier_enricher.infer(...)

# Apply when present; 1.0 confidence. filecite:turn35file12
