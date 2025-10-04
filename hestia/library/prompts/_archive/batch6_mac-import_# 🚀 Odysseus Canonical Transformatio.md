"# 🚀 **Odysseus Canonical Transformation & Normalization Prompt for HESTIA Alpha Sensor Registry**

---

## 📜 **Primary Objective**

Perform a **single, complete, one-way transformation** of the current `sensor_signal_plane.json`, following the **HESTIA Alpha Sensor Registry Schema**, ensuring:

- Full **schema compliance** per the Signal Plane definition
- **Normalization** of all critical fields
- **Canonical ID uniqueness**
- **Confidence metric completion**
- **Validator-ready, publication-quality output**
- **Zero invention of unknown data** — use `null` when necessary
- **Greek tier suffix enforcement** (`α`, not ""alpha"")

---

## 🧹 **Phase 1: Field Cleanup and Normalization**

Apply these normalization passes:

| # | Task | Notes |
|:--|:--|:--|
| 1.1 | Fill in missing `signal_type` from `device_class` or `role` when blank | e.g., `""contact""` or `""occupancy""` based on role |
| 1.2 | Enforce unique `canonical_id` per integration path | No duplicate canonical IDs across fallback paths |
| 1.3 | Ensure `firmware`, `model_name`, `mac`, `ipv4`, `ipv6`, `ssid` are present or explicitly `null` | No omissions |
| 1.4 | Normalize `platform`, `device_class`, `type` fields to valid options only | (`binary_sensor`, `sensor`, `update`, etc.) |
| 1.5 | If `availability_sensor` missing but fallback exists, set it to `null` explicitly | No blanks |
| 1.6 | Ensure `confidence_metrics` blocks are present and populated for all devices | Entity, device, and relationship |
| 1.7 | Standardize feature listings under `capabilities` | Follow strict entity structure |
| 1.8 | Validate room/area fields (`room_id`, `room_area`) follow snake_case and match logical location |

---

## 🏛️ **Phase 2: Schema Transformation**

Restructure devices strictly according to the **Target Schema Structure**:

- Follow **`metadata`**, **`location`**, **`device_info`**, **`integration`**, **`capabilities`** blocks exactly as defined
- Nest capabilities cleanly under `capabilities` (previously called `features`)
- Support multi-class devices under `integration_stack` (like Aeotec multipurpose)
- Use `""availability_sensor"": null` if missing
- Respect preferred vs fallback integrations; fallback must never overwrite primary canonical ID
- Consolidate any inconsistent or multi-source signal references carefully

---

## 🔥 **Phase 3: Governance and Protection**

Mandatory in the final output:

| Rule | Description |
|:--|:--|
| Canonical ID Suffix | Always Greek letter (`_α`) for alpha tier |
| No Ghost Entities | Every `entity_id` must exist if referenced |
| No Invented Data | If data missing, populate `null`, not made-up values |
| Confidence Check | Any sensor under 75% confidence should be flagged (`requires_review: true`) |
| Availability Linking | If device has fallback, check presence of availability sensor or explicitly set to `null` |

---

## 🛡️ **Phase 4: Versioning Metadata**

At the top of the finalized file, inject:

```json
""_meta"": {
  ""version"": ""v1.0"",
  ""build_date"": ""2025-04-27T18:00:00Z"",
  ""build_by"": ""Odysseus"",
  ""schema"": ""https://hestia.local/schemas/device_registry.schema.json""
}
```

---

## 📋 **Process Workflow**

1. Parse the source `sensor_signal_plane.json`
2. Identify each device type (Full Device, Device ID object, Flat Entity)
3. Apply Phase 1 Normalization rules
4. Apply Phase 2 Schema Restructuring
5. Validate compliance against Target Schema
6. Enforce Phase 3 Governance rules
7. Output the finalized, hardened, validator-ready `sensor_signal_plane.json`
8. Log and output any transformation warnings (confidence under threshold, missing availability)

---

# Confidence Tracking Instructions

You will perform a complete transformation job, going in sequential order from top to bottom, until the level of reported confidence is too low to be considered relevant (i.e. confidence level).
When performing the HESTIA sensor registry schema transformation, I want you to maintain a structured confidence scoring system to track your certainty about each transformation decision. This will help prioritize entries that may need human verification.

## Confidence Scoring System

For each device entry you transform, track confidence at three levels:

1. Entity-level confidence (0-100%): How certain you are about the correctness of individual field mappings
2. Device-level confidence (0-100%): Overall confidence in the complete device transformation
3. Relationship confidence (0-100%): Confidence in the grouping decisions (which entities belong to which devices)

## Scoring Criteria

Use these criteria to determine confidence scores:

| Confidence Level | Score | Description |
|------------------|-------|-------------|

| High | 80-100% | Clear 1:1 mapping from source to target, minimal inference needed |
| Medium | 50-79% | Requires some inference but has strong supporting evidence |
| Low | 20-49% | Requires significant inference with limited supporting data |
| Uncertain | 0-19% | Mostly guesswork, insufficient data to make reliable determination |

## Confidence Factors

Adjust confidence scores based on these factors:

- -30%: Required fields missing with no clear way to derive them
- -20%: Conflicting information between related entities
- -15%: Entity grouping requires inference rather than explicit IDs
- -10%: Multiple possible interpretations for field values
- +20%: Explicit matches between source and target fields
- +15%: Clear device_id groupings present
- +10%: Consistent naming patterns that follow HESTIA conventions

Recommended Confidence Thresholds

For the HESTIA sensor registry transformation, I recommend implementing a multi-tier threshold system:

Primary Stop Threshold: 40% Overall Device Confidence

The GPT should completely halt the transformation job and request human intervention when:

- Any device-level confidence score falls below 40%
- This indicates fundamental uncertainty about how to properly transform the device

Selective Skip Thresholds

You should skip individual devices but continue with others when:

- Device-level confidence is between 40-55%
- Relationship confidence falls below 50%
- More than 3 required fields have confidence below 60%

Review Flag Thresholds

You should flag for later human review but complete the transformation when:

- Device-level confidence is between 55-70%
- Any required field has confidence below 60%
- Relationship confidence is between 50-65%

Rationale

40% as the hard stop: At this level, the transformation becomes more guesswork than informed mapping, risking system integrity
55% for selective skipping: Below this, transformation quality drops significantly while still being somewhat reasonable
70% for review flagging: This catches borderline cases where the transformation is likely correct but warrants verification
These tiered thresholds balance:

1. Automation efficiency (not stopping too frequently)
2. Data integrity (not allowing highly uncertain transformations)
3. Human workload optimization (focusing human review on truly ambiguous cases)

For transparency, we would like you to report:

- Total devices processed
- Devices completely skipped (below 40%)
- Devices transformed but flagged for review (below 70%)
- Highest and lowest confidence scores encountered

This gives us both clear action thresholds and visibility into the overall confidence distribution of the transformation process.

## Reporting Format

Include a confidence section with each transformed device entry:

```json
"confidence_metrics": {
  "entity_confidence": {
    "score": 85,
    "factors": ["Clear entity_id match", "Explicit device_id reference"],
    "uncertain_fields": ["integration.preferred_protocol", "metadata.added_date"]
  },
  "device_confidence": {
    "score": 75,
    "factors": ["Multiple consistent entities", "Missing firmware data"]
  },
  "relationship_confidence": {
    "score": 90,
    "factors": ["Explicit device_id references"]
  },
  "requires_review": false
}

## Review Flagging

Automatically flag entries for human review when:
- Any confidence score falls below 50%
- The average of all three scores is below 70%
- Any required field has been filled with an inferred value at low confidence

## Integration with Transformation Process

After performing each device transformation:
1. Calculate confidence scores for that device
2. Document any uncertain fields or inferences made
3. Flag entries that need human review
4. Include the confidence metrics in your response
This will help us prioritize which transformations need additional verification and provide transparency about the transformation process.

---

## 🎯 **Final Output**

- `sensor_signal_plane.json` (only file maintained)
- Fully normalized
- Version-tagged
- Schema-compliant
- Single authoritative registry moving forward

---

# 🧠 **Odysseus Reminder**

> **You are preserving architecture, not just cleaning files.  
You are setting the future backbone of the HESTIA Signal Plane.**  
One file. One truth. Full traceability.

---"