---
id: ADR-0002
title: Home Assistant Jinja Pattern Normalization
slug: home-assistant-jinja-pattern-normalization
status: Accepted
related: []
supersedes: []
last_updated: '2025-10-15'
date: 2025-09-11
decision: 'The following patterns should be used to normalize and gate Jinja logic:'
tags:
- jinja
- patterns
- normalization
- templates
- automation
- adr
- error-handling
- datetime
- state
- comparison
author: Evert Appels
---


# ADR-0002: Home Assistant Jinja Pattern Normalization

## Table of Contents
1. Context
2. Decision
3. Enforcement
4. Tokens
5. Last updated

## 1. Context
Home Assistant automations and templates often use Jinja2 for logic, but raw state values and datetime handling can lead to errors and edge cases. This ADR documents normalization patterns and rules for robust, error-free Jinja logic in Home Assistant YAML.

## 2. Decision
The following patterns should be used to normalize and gate Jinja logic:

### Patterns
- **direct_comparison_to_now**
  - Match:
    ```jinja
    {{ now() > states('input_datetime.foo') }}
    ```
  - Replace:
    ```jinja
    {% set raw = states('input_datetime.foo') %}
    {% set t = as_datetime(raw) if raw not in ['unknown','unavailable',''] else None %}
    {{ t is not none and now() > t }}
    ```

- **compare_two_parsed_datetimes**
  - Match:
    ```jinja
    {{ as_datetime(x) > as_datetime(y) }}
    ```
  - Replace:
    ```jinja
    {% set xdt = as_datetime(x) %}
    {% set ydt = as_datetime(y) %}
    {{ xdt is not none and ydt is not none and xdt > ydt }}
    ```

- **mixing_aware_naive**
  - Match:
    ```jinja
    {% set t = strptime(some_string, '%Y-%m-%d %H:%M:%S') %}
    {{ now() > t }}
    ```
  - Replace:
    ```jinja
    {% set t = as_datetime(some_string) %}
    {{ t is not none and now() > t }}
    ```

- **timestamp_math_without_guards**
  - Match:
    ```jinja
    {{ (now() - as_datetime(x)).total_seconds() > 900 }}
    ```
  - Replace:
    ```jinja
    {% set t = as_datetime(x) %}
    {{ t is not none and (now() - t).total_seconds() > 900 }}
    ```

## 3. Enforcement
- Always gate on `is not none` for datetime and state values.
- Normalize inputs from states with `raw not in ['unknown','unavailable','']`.
- Use `now()` everywhere (HA returns timezone-aware) unless you explicitly standardize both sides to UTC.

## 4. Tokens
- `now()`: Home Assistant's timezone-aware current time.
- `as_datetime(x)`: Converts string or state to datetime, returns `None` if invalid.
- `raw`: Raw state value from Home Assistant.
- `is not none`: Guard for valid values.

---
_Last updated: 2025-09-11_
