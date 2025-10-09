---
id: prompt_20251001_46a78f
slug: gpt-output-schema-ha-config-declaration-mapper
title: Gpt Output Schema Ha Config Declaration Mapper
date: '2025-10-01'
tier: "\u03B2"
domain: operational
persona: generic
status: candidate
tags: []
version: '1.0'
source_path: gpt-validate-config/gpt-output-schema-ha-config-declaration-mapper.json
author: Unknown
related: []
last_updated: '2025-10-09T02:33:25.555513'
redaction_log: []
---

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Home Assistant Configuration Mapping Output",
  "type": "object",
  "properties": {
    "unique_id": {
      "type": "string"
    },
    "configuration_line_number": {
      "type": "integer"
    },
    "configuration_value": {
      "type": "string"
    },
    "configuration_target": {
      "type": "string"
    },
    "declaration_type": {
      "type": "string",
      "enum": [
        "include",
        "include_dir_list",
        "include_dir_merge_list",
        "include_dir_named",
        "include_dir_merge_named",
        "none"
      ]
    },
    "is_valid": {
      "type": "boolean"
    },
    "target_type": {
      "type": "string",
      "enum": [
        "file",
        "folder",
        "none"
      ]
    },
    "target_value": {
      "type": "string"
    },
    "target_content": {
      "type": "string",
      "enum": [
        "sensor",
        "template",
        "automation",
        "script",
        "input",
        "group",
        "package",
        "other",
        "unknown"
      ]
    },
    "content_valid": {
      "type": "boolean"
    },
    "parent_block": {
      "type": [
        "string",
        "null"
      ]
    },
    "error_reason": {
      "type": [
        "string",
        "null"
      ]
    },
    "recursion_depth": {
      "type": "integer",
      "minimum": 1
    }
  },
  "required": [
    "unique_id",
    "configuration_line_number",
    "configuration_value",
    "configuration_target",
    "declaration_type",
    "is_valid",
    "target_type",
    "target_value",
    "target_content",
    "content_valid",
    "recursion_depth"
  ]
}
