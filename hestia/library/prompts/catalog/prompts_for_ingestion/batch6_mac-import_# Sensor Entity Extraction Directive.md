# Sensor Entity Extraction Directive

## Objective
Extract a comprehensive, structured list of ALL sensor entities from the provided YAML configuration files. Your goal is to create a detailed, normalized catalog of sensors across the HESTIA system.

## Extraction Guidelines

### 1. Sensor Entity Identification
- Look for sensors defined with:
  - `unique_id`
  - `name`
  - `state` or `value_template`
  - Specific HESTIA tier suffixes (α, β, γ, δ, ε, ζ)

### 2. Capture Metadata
For each sensor, compile the following information:
- **Unique ID**: The system-unique identifier
- **Name**: Human-readable name
- **Canonical ID**: If present
- **Tier**: Greek letter abstraction tier (α, β, γ, δ, ε, ζ)
- **Domain**: Functional category (e.g., motion, temperature, humidity)
- **Subsystem**: HESTIA subsystem (e.g., HERMES, THEIA, SOTERIA)
- **File Source**: Original configuration file path
- **Unit of Measurement**: If specified
- **Device Class**: If specified

### 3. Extraction Strategy
- Systematically parse each YAML file
- Handle nested structures in files like `climate_sensors.yaml`
- Look for sensors in:
  - `template` sections
  - Directly defined sensor blocks
  - Metadata and diagnostic sensor definitions

### 4. Normalization Rules
- Standardize naming conventions
- Resolve any duplicate or conflicting entries
- Maintain the HESTIA tier hierarchy

### 5. Output Format
Produce a JSON structure with the following schema:
```json
{
  "sensors": [
    {
      "unique_id": "string",
      "name": "string",
      "canonical_id": "string",
      "tier": "string",
      "domain": "string",
      "subsystem": "string",
      "file_source": "string",
      "unit_of_measurement": "string",
      "device_class": "string"
    }
  ]
}
```

## Special Considerations
- Handle cases where sensors are dynamically generated
- Pay attention to diagnostic and metadata sensors
- Capture sensors from these files:
  - `climate_sensors.yaml`
  - `sensor_motion_diagnostic.yaml`
  - `aether_binary_trend_flags.yaml`
  - `soteria_config.yaml`
  - `soteria_logic.yaml`

## Processing Instructions
1. Read each YAML file carefully
2. Extract sensors using the guidelines above
3. Merge and deduplicate the results
4. Validate the completeness of the extraction
5. Provide a summary of total sensors found and any extraction challenges

## Example of Desired Output
```json
{
  "sensors": [
    {
      "unique_id": "bedroom_motion_score",
      "name": "Bedroom Motion Score",
      "canonical_id": "sensor_bedroom_motion_score_γ",
      "tier": "γ",
      "domain": "motion",
      "subsystem": "HESTIA",
      "file_source": "/config/hestia/core/sensor_motion_diagnostic.yaml",
      "unit_of_measurement": "score",
      "device_class": null
    }
  ]
}
```

## Deliverable
- Comprehensive JSON list of all sensors
- A brief report explaining the extraction process
- Any notes on sensors that required special handling

Are you ready to begin the sensor entity extraction process?