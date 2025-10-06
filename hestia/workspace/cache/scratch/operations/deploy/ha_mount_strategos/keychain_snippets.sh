#!/usr/bin/env bash
# Keychain lookup helper snippets for macOS
# Drop these functions into a mount helper script to retrieve SMB passwords
# from the macOS Keychain instead of prompting interactively.

set -euo pipefail

# Try finding a generic password by label (most common for stored secrets)
# Usage: pw=$(get_password_by_label "ha_nas_system")
get_password_by_label() {
  local label="$1"
  # prefer generic-password (often used for app/generic secrets)
  if security find-generic-password -l "$label" -w 2>/dev/null; then
    security find-generic-password -l "$label" -w 2>/dev/null
    return 0
  fi
  # fallback to internet-password (useful when secret was stored with a server/account)
  if security find-internet-password -l "$label" -w 2>/dev/null; then
    security find-internet-password -l "$label" -w 2>/dev/null
    return 0
  fi
  return 1
}

# Lookup by server and account (internet password)
# Usage: pw=$(get_password_by_server_account "192.168.0.104" "babylonrobot")
get_password_by_server_account() {
  local server="$1" account="$2"
  security find-internet-password -s "$server" -a "$account" -w 2>/dev/null
}

# Example helper that tries several strategies and falls back to interactive read
# Usage: pw=$(pw_lookup_or_prompt "ha_nas_system" "192.168.0.104" "babylonrobot")
pw_lookup_or_prompt() {
  local label="$1" server="$2" account="$3" pw
  if pw=$(get_password_by_label "$label" 2>/dev/null); then
    printf '%s' "$pw"
    return 0
  fi
  if [ -n "$server" ] && [ -n "$account" ]; then
    if pw=$(get_password_by_server_account "$server" "$account" 2>/dev/null); then
      printf '%s' "$pw"
      return 0
    fi
  fi
  # fallback: interactive prompt on /dev/tty
  if [ -r /dev/tty ]; then
    printf "Keychain lookup failed for '%s'.\n" "$label" >&2
    read -r -s -p "SMB password for ${account:-$label}: " pw </dev/tty
    echo >&2
    printf '%s' "$pw"
    return 0
  fi
  return 1
}

# Safe URL-encoding helper (keeps behavior consistent with existing script)
urlenc() {
  local s="$1" i ch out hex
  out=""
  for ((i=0;i<${#s};i++)); do
    ch=${s:i:1}
    case "$ch" in
      [a-zA-Z0-9._~-]) out+="$ch" ;;
      *) printf -v hex '%%%02X' "'${ch}"; out+="$hex" ;;
    esac
  done
  printf '%s' "$out"
}

# Example integration (commented out) --------------------------------------------------
# LABEL=ha_nas_system
# SERVER=192.168.0.104
# ACCOUNT=babylonrobot
# if PW=$(pw_lookup_or_prompt "$LABEL" "$SERVER" "$ACCOUNT"); then
#   PW_ENC=$(urlenc "$PW")
#   unset PW   # clear the plaintext variable once encoded
# else
#   echo "ABORT_EMPTY_CREDS" >&2
#   exit 70
# fi
# -------------------------------------------------------------------------------------
