---
id: prompt_20251001_6f6dc8
slug: batch6-mac-import-prompt-diagnostic-regactor-harde
title: Batch6 Mac Import Prompt Diagnostic Regactor Harden
date: '2025-10-01'
tier: "beta"
domain: operational
persona: promachos
status: candidate
tags:
- diagnostic
version: '1.0'
source_path: batch6_mac-import_prompt_diagnostic_regactor_harden.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:24.445823'
redaction_log: []
---

prompt:
  role: Promachos
  phase: DIAGNOSTIC_REFACTOR + SECURITY_HARDEN
  intent: Execute a full-spectrum diagnostic hardening and telemetry consolidation plan for macOS-based Glances telemetry via Home Assistant
  execution_mode: generate
  action_plan:
    - id: netlock_rest
      description: |
        🔒 Harden REST/Glances access exposed via Tailscale:
        • Enforce firewall rule to restrict access to Home Assistant IP only
        • Enable Glances password protection if disabled
        • Proxy Glances through HTTPS or restrict via Tailscale ACL

    - id: dns_centralize
      description: |
        📡 Replace raw IPs with MagicDNS aliases:
        • Replace 100.92.58.104 with macbook.reverse-beta.ts.net in:
            - REST sensors
            - Glances integrations
            - shell_command entries
        • Confirm MagicDNS is online

    - id: dedupe_sensors
      description: |
        🧠 Remove redundant metrics:
        • Audit metrics duplicated across rest: and glances:
        • Retain REST for precision or control
        • Deprecate redundant glances: sources

    - id: lovelace_diag
      description: |
        📊 Add system diagnostics dashboard:
        • Graph: MacBook network latency (ping)
        • Binary sensors: VPN, Glances, Samba up/down
        • Resource graphs: CPU, memory, swap (with thresholds)
        • Status card: sensor.macbook_diagnostic_status

    - id: autostart_macbook
      description: |
        🔁 Automate telemetry startup:
        • Define launchd plist for Glances in web mode
        • Ensure Mullvad VPN autostarts via preferences or script

    - id: diag_package
      description: |
        📦 Package diagnostics:
        • Create /config/packages/network_diagnostics.yaml
        • Migrate sensors, shell_commands, automations
        • Use !include_dir_merge_named in configuration.yaml

    - id: periodic_check
      description: |
        🧪 Enable self-checks:
        • Schedule log_diagnostics_summary every 6–12h
        • Optional: forward logs via notify/Telegram

    - id: syntax_upgrade
      description: |
        💡 Enforce HA 2024.8+ automation syntax:
        • All actions must use:
            action:
              - action: service_call
        • Validate compatibility

  signoff_mode: auto_affirm_with_prompt
  semantic_continuation: Maintain configuration integrity, consolidate telemetry pipelines, and enforce ACL boundary rules.
  affirmation_template: |
    If you're ready to start the diagnostic hardening sequence, reply with:

    ```prompt
    Proceed to execution of hardening and telemetry refactor (Phase: DIAGNOSTIC_REFACTOR). Ensure full YAML consolidation and DNS alias rewiring.
    ```

    To pause for clarification or adjust scope, reply with:

    ```prompt
    Hold on DIAGNOSTIC_REFACTOR. Let’s review target entries or Glances authentication config first.
    ```

