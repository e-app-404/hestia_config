---
id: prompt_20251008_5e4a35
slug: etcautohasmb
title: /etc/auto_ha.smb
date: '2025-10-08'
tier: "beta"
domain: operational
persona: generic
status: candidate
tags: []
version: '1.0'
source_path: autofs/auto_ha.smb
author: Unknown
related: []
last_updated: '2025-10-09T01:44:27.065641'
redaction_log: []
---

# /etc/auto_ha.smb
# Direct map for Home Assistant config share
# Default to Bonjour (mDNS); switch to Tailscale FQDN if preferred.
#/n/ha  -fstype=smbfs ://homeassistant.reverse-beta.ts.net/config   # Tailscale option
/n/ha   -fstype=smbfs ://homeassistant.local/config

