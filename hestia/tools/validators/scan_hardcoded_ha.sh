#!/usr/bin/env bash
set -euo pipefail
# Search the repo for literal /n/ha outside docs and skip common binary/image file types
rg -n --hidden --glob '!.git' --glob '!hestia/docs/**' --glob '!**/*.png' --glob '!**/*.jpg' --glob '!**/*.jpeg' --glob '!**/*.gif' --glob '!**/*.svg' '/n/ha' . && { echo "ERROR: hard-coded /n/ha found outside docs"; exit 1; } || { echo "OK: no hard-coded /n/ha outside docs"; }
