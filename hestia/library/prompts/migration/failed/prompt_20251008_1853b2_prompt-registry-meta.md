---
id: prompt_20251008_1853b2
slug: prompt-registry-meta
title: Prompt Registry Meta
date: '2025-10-08'
tier: "α"
domain: validation
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: meta/prompt_registry_meta.json
author: Unknown
related: []
last_updated: '2025-10-09T01:44:27.591555'
redaction_log: []
---

{
  "$schema": "https://json-schema.org/hestia_v7/2025-04/schema",
  "title": "Prompt Definition Schema",
  "type": "object",
  "required": [
    "prompt_id",
    "prompt_title",
    "deployment_context",
    "usage_class",
    "Meta-function",
    "prompt",
    "version"
  ],
  "properties": {
    "prompt_id": {
      "type": "string"
    },
    "prompt_title": {
      "type": "string"
    },
    "deployment_context": {
      "type": "string"
    },
    "usage_class": {
      "type": "string"
    },
    "Meta-function": {
      "type": "string"
    },
    "prompt_type": {
      "type": [
        "string",
        "null"
      ]
    },
    "prompt_category": {
      "type": [
        "string",
        "null"
      ]
    },
    "prompt_use_cases": {
      "type": [
        "string",
        "null"
      ]
    },
    "prompt": {
      "type": "string"
    },
    "prompt_response_example": {
      "type": [
        "string",
        "null"
      ]
    },
    "Tags": {
      "type": [
        "string",
        "null"
      ]
    },
    "score": {
      "type": [
        "number",
        "null"
      ]
    },
    "version": {
      "type": [
        "string",
        "number"
      ]
    },
    "validation_criterion": {
      "type": [
        "string",
        "null"
      ]
    },
    "date_created": {
      "type": [
        "string",
        "null"
      ],
      "format": "date"
    },
    "date_modified": {
      "type": [
        "string",
        "null"
      ],
      "format": "date-time"
    }
  }
}
