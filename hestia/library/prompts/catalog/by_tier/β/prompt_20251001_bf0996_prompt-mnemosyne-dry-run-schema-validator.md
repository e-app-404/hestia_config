---
id: prompt_20251001_bf0996
slug: prompt-mnemosyne-dry-run-schema-validator
title: "\U0001F9E0 Prompt: Mnemosyne Dry-Run Schema Validator"
date: '2025-10-01'
tier: "\u03B2"
domain: diagnostic
persona: generic
status: candidate
tags: []
version: '1.0'
source_path: batch 4/batch4-prompt_mnemosyne_dry_run_schema_validator_20250528.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:27.153313'
redaction_log: []
---

`id: prompt_mnemosyne_dry_run_schema_validator_20250528`

# 🧠 Prompt: Mnemosyne Dry-Run Schema Validator

Given two dry-run outputs or JSON diagnostics from different snapshots, compare their structure and semantic content. Identify any:

- Added or removed keys
- Type mismatches
- Output count deviations
- Missing fallback stubs

Return a structured diff report with severity ratings.

