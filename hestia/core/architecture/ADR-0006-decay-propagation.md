---
title: ADR-0006: Decay and Propagation Logic Contract
date: 2025-09-11
status: Pending Validation
---

# ADR-0006: Decay and Propagation Logic Contract

## Table of Contents
1. Context
2. Decision
3. Enforcement
4. Tokens
5. Last updated

## 1. Context
This ADR formalizes the canonical rules for decay and propagation logic in Home Assistant. These rules govern how presence, motion, and occupancy signals decay and propagate across areas, subareas, and containers, affecting automations, sensors, and entity inference.

## 2. Decision
### Included Artifacts
- `domain/automations/decay_automation.yaml`
- Related sensors, binary_sensors, and templates in all domains

### Scope
- Decay profiles: timeouts, confidence reduction, and retention logic for signals
- Propagation rules: directionality, aggregation, and boundary crossing for motion, presence, and occupancy
- Tags: `decay`, `boundary`, `aggregation`, `retention`, `propagation`

### Example Tokens
- `decay_profile`, `decay_rate`, `timeout`, `aggregate_method`, `propagation_direction`, `signal_type`, `confidence`, `retention`

## 3. Enforcement
- All referenced YAML logic must be validated against live automations and entity state transitions.
- Changes to decay or propagation require a new contract version.
- This ADR is pending validation and subject to revision after full coverage and consistency checks.

## 4. Tokens
- `decay_profile`, `propagation_rules`, `aggregate_method`, `timeout`, `confidence`, `retention`, `signal_type`

---
_Last updated: 2025-09-11_
