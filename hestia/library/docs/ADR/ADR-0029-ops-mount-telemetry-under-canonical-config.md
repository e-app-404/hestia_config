---
id: ADR-0029
slug: ops-mount-telemetry-under-canonical-config
title: Operational Mount & Telemetry under Canonical /config
status: Accepted
created: 2025-10-20
amends:
  - ADR-0024
supersedes:
  - ADR-0022
---

# Decision
Implement ADR-0024 operationally on macOS via APFS synthetic `/config` → `/System/Volumes/Data/homeassistant`, user-level LaunchAgent, Keychain-backed non-interactive SMB mounts (hostname + IP entries), and local-only mount telemetry. All tools, scripts, and docs MUST reference `/config`.

# Rationale
Separates policy (ADR-0024) from operational implementation. Eliminates legacy path drift, ensures predictable mounting, and provides binary health signals.

# Normative Rules
- `/config` is the sole public interface (per ADR-0024).
- Mount target is `/System/Volumes/Data/homeassistant` only.
- Keychain entries MUST exist for `homeassistant.local` and active IP, with trusted apps: `/sbin/mount_smbfs`, `/usr/bin/smbutil`, NetAuthAgent, Terminal.
- LaunchAgent runs as user, logs to `~/Library/Logs/Hestia`.
- Telemetry is local-only; payload includes `realpath(/config)`, `mounted`, `write_ok`, `agent_loaded`, `agent_exit_code`; no secrets.

# Compliance & Validation
- Guard scripts pass in RO/RW contexts.
- Linter rejects `$HOME/`, `~/hass`, `/Volumes/`, `/n/ha`, `actions-runner/.+?/hass`, excluding `ADR/deprecated/**` and `library/docs/ADR-imports/**`.
- Binary health checks green on macOS, containers, and CI.

# Consequences
Removes ambiguity from ADR-0022; establishes a single operational reference.

# Backout
Re-enable transitional `/homeassistant -> /config` symlink only as a temporary measure; policy remains ADR-0024.


```patch
## Assumptions

* macOS operator host runs current macOS with LaunchAgents supported in `~/Library/LaunchAgents`.
* The Samba add-on on Home Assistant exposes the `config` share and authenticates with username/password stored in macOS Keychain (entries for both `homeassistant.local` and its current IP).
* `/config` resolves to `/System/Volumes/Data/homeassistant` via synthetic mapping; `/config` must be treated as the only public interface path.
* CI can operate in read-only mode when `REQUIRE_CONFIG_WRITABLE=0`.

## Touchpoints Checklist

* macOS filesystem interface (`/config` synthetic → Data path).
* SMB mount policy (hostname/IP, non-interactive auth, permissions modes).
* LaunchAgent (user scope, retry/backoff, sleep/wake/network awareness, logging).
* Keychain governance (creation, rotation, auto-trust for required binaries).
* Telemetry & logs (schema, retention, location).
* Guards, linters, fixers (RO/RW, exclusions for ADR imports).
* Home Assistant references (`shell_command`, backups, recorder paths) pinned to `/config`.
* VS Code/devcontainer/compose/CI mounting to `/config`.
* Spotlight & watcher behavior on network share.
* Backout and recovery procedures.

---

## Patch Set

### ADR/ADR-0029-ops-mount-telemetry-under-canonical-config.md

````markdown
---
id: ADR-0029
slug: ops-mount-telemetry-under-canonical-config
title: Operational Mount & Telemetry under Canonical /config
status: Accepted
created: 2025-10-20
context: production
amends:
  - ADR-0024
supersedes:
  - ADR-0022
stakeholders:
  - operator_host: macOS (user: evertappels)
  - ha_stack: HA Core/Supervisor
  - ci: GitHub Actions
---

# 1) Decision

Operationalize ADR-0024 on macOS using:
- APFS synthetic mapping so `/config` resolves to `/System/Volumes/Data/homeassistant`.
- User-level LaunchAgent to mount the HA Samba `config` share to the Data path.
- Keychain-backed, non-interactive SMB authentication (hostname **and** IP entries; trusted apps).
- Local-only mount telemetry with a strict, minimal schema.
All tools, scripts, docs, and automation **MUST** reference `/config` exclusively.

# 2) Rationale

Separates policy (ADR-0024) from runbook. Removes legacy path drift, ensures deterministic mounting, and provides binary health signals without leaking secrets.

# 3) Scope

Covers macOS operator host behavior, logging/telemetry, and integration points with CI and HA runtime that depend on the canonical path. Does not alter HA network/export settings.

# 4) Normative Rules

**Canonical Interface**
1. `/config` is the sole public interface path (see ADR-0024). No `$HOME`, `~/hass`, `/Volumes/...`, `/n/ha`, or actions-runner paths in code/docs.

**Mount Target**
2. The only mount target is `/System/Volumes/Data/homeassistant` (the “Data path”). `/config` must not be used as a mountpoint.

**SMB & Auth**
3. Credentials MUST exist in Keychain for both `homeassistant.local` and the active IP (e.g., `192.168.0.129`), protocol `smb`.
4. Trusted applications MUST include:
   - `/sbin/mount_smbfs`
   - `/usr/bin/smbutil`
   - `/System/Library/CoreServices/NetAuthAgent.app/Contents/MacOS/NetAuthAgent`
   - `/System/Applications/Utilities/Terminal.app/Contents/MacOS/Terminal`
5. Mounts MUST be non-interactive. If a prompt appears, the Keychain is out of policy and MUST be remediated.

**LaunchAgent**
6. Runs as the user, with `KeepAlive.NetworkState=true`, `StartInterval=60`, and logs to `~/Library/Logs/Hestia`.
7. The agent MUST mount onto the Data path and **never** onto `/config`.
8. The agent MUST implement bounded retry/backoff and safe unmount on logout/shutdown.

**Permissions & Modes**
9. Present file/dir modes via client options: files `0644`, dirs `0755`. The mountpoint directory owner MUST be `${USER}:staff`.

**Spotlight & Watchers**
10. Spotlight indexing MUST be disabled on the Data path mount to avoid churn.
11. Editor/file-watcher limits SHOULD be tuned to avoid polling overload on SMB volumes.

**Telemetry**
12. Telemetry is local-only, JSON lines, no secrets. Schema defined in §7. Retention ≤ 30 days or 50 MB, whichever first.

**Compliance**
13. Guard scripts MUST pass in RO/RW contexts; CI MUST set `REQUIRE_CONFIG_WRITABLE=0` for read-only jobs.
14. Linter MUST reject: `\$HOME/`, `~/hass`, `/Volumes/`, `/n/ha`, `actions-runner/.+?/hass`; with exclusions for `ADR/deprecated/**` and `library/docs/ADR-imports/**`.

# 5) Implementation Summary (Authoritative)

- `/etc/synthetic.conf` contains: `config\thomeassistant`.
- Data path exists: `/System/Volumes/Data/homeassistant`, owned by `${USER}:staff`.
- LaunchAgent `com.hestia.mount.homeassistant.plist` executes `~/bin/ha-mount.sh`.
- `ha-mount.sh` mounts `//${USER}@<host-or-ip>/config` to the Data path using Keychain (no prompts), applies modes, disables Spotlight, emits telemetry.
- Health tools: `bin/require-config-root`, `bin/config-health`, `tools/lint_paths.sh`.

# 6) Validation (Binary)

Must pass:
- `stat -f '%HT' /config` → directory or symlink resolving to Data path.
- `python3 -c 'import os;print(os.path.realpath("/config"))'` → `/System/Volumes/Data/homeassistant`.
- `mount | grep ' /System/Volumes/Data/homeassistant .*smbfs'` → exactly one mount active.
- `REQUIRE_CONFIG_WRITABLE=0 bin/require-config-root` → exit 0.
- `tools/lint_paths.sh` → no findings.
- Telemetry file updated on each (re)mount with schema in §7.

# 7) Telemetry Schema (Local-only)

```json
{
  "ts": "RFC3339",
  "host": "macbook",
  "iface": "/config",
  "realpath": "/System/Volumes/Data/homeassistant",
  "mounted": true,
  "mount_fs": "smbfs",
  "mount_src": "//evertappels@homeassistant.local/config",
  "ip": "192.168.0.129",
  "write_ok": true,
  "agent_loaded": true,
  "agent_pid": 12345,
  "agent_exit_code": 0,
  "last_error": "",
  "keychain_host_entry": true,
  "keychain_ip_entry": true
}
````

Retention policy: rotate daily, keep ≤ 30 days or ≤ 50 MB total.

# 8) Migration

* **Supersede ADR-0022**. Move to `ADR/deprecated/` with `status: Superseded` and `superseded_by: ADR-0029`.
* Replace any `ha_mount_*` scripts from ADR-0022 with `~/bin/ha-mount.sh`.
* Re-issue Keychain entries for both hostname and IP, with trusted apps (§4).

# 9) Risks & Mitigations

* **Host/IP drift** → maintain both Keychain entries; agent retries on DNS failure.
* **Interactive prompts** → Keychain trust missing; remediate entries or reset and re-add.
* **Editor watcher load** → disable Spotlight; constrain watcher settings for SMB paths.
* **Stale mounts** → agent unmounts on logout/shutdown; health check alerts in logs.

# 10) Backout

Temporary allowance: `/homeassistant -> /config` symlink may be enabled to maintain continuity during incident response. Policy remains `/config` (ADR-0024).

---

````

### Appendices (referenced by ADR-0029)

#### Appendix A — LaunchAgent (user) `~/Library/LaunchAgents/com.hestia.mount.homeassistant.plist`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.hestia.mount.homeassistant</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/evertappels/bin/ha-mount.sh</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>NetworkState</key><true/></dict>
  <key>StartInterval</key><integer>60</integer>
  <key>LimitLoadToSessionType</key><array><string>Aqua</string></array>
  <key>ProcessType</key><string>Background</string>
  <key>StandardOutPath</key><string>/Users/evertappels/Library/Logs/Hestia/ha-mount.out</string>
  <key>StandardErrorPath</key><string>/Users/evertappels/Library/Logs/Hestia/ha-mount.err</string>
</dict>
</plist>
````

#### Appendix B — Mount Script `~/bin/ha-mount.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-homeassistant.local}"
IP="${IP:-}"
SHARE="${SHARE:-config}"
MNT="/System/Volumes/Data/homeassistant"
LOG_DIR="$HOME/Library/Logs/Hestia"
TELEM="$LOG_DIR/mount_telemetry.jsonl"

mkdir -p "$LOG_DIR"
sudo mkdir -p "$MNT"
sudo chown "$USER":staff "$MNT"

# choose source: prefer hostname; fallback to IP if provided
SRC="//$USER@$HOST/$SHARE"
if ! ping -t 1 -c 1 "$HOST" >/dev/null 2>&1 && [[ -n "${IP}" ]]; then
  SRC="//$USER@$IP/$SHARE"
fi

# clean stale mount
diskutil unmount force "$MNT" >/dev/null 2>&1 || true

# mount non-interactively (Keychain-backed)
# file/dir modes presentable via client; SMB honors server-side ACLs
/sbin/mount_smbfs -N -f 0644 -d 0755 "$SRC" "$MNT" || {
  printf '{"ts":"%s","host":"macbook","iface":"/config","realpath":"%s","mounted":false,"mount_fs":"smbfs","mount_src":"%s","write_ok":false,"agent_loaded":true,"agent_exit_code":64,"last_error":"mount_failed"}\n' \
    "$(date -u +%FT%TZ)" "$MNT" "$SRC" >>"$TELEM"
  exit 64
}

# disable Spotlight indexing (performance)
mdutil -i off "$MNT" >/dev/null 2>&1 || true

# telemetry
REAL="$(python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "$MNT" 2>/dev/null || echo "$MNT")"
WRITE_OK=1
touch "$MNT/.mount_write_test" 2>/dev/null || WRITE_OK=0
[[ $WRITE_OK -eq 1 ]] && rm -f "$MNT/.mount_write_test" 2>/dev/null || true

printf '{"ts":"%s","host":"macbook","iface":"/config","realpath":"%s","mounted":true,"mount_fs":"smbfs","mount_src":"%s","ip":"%s","write_ok":%s,"agent_loaded":true,"agent_pid":%d,"agent_exit_code":0,"last_error":"","keychain_host_entry":true,"keychain_ip_entry":%s}\n' \
  "$(date -u +%FT%TZ)" "$REAL" "$SRC" "${IP:-""}" "$WRITE_OK" "$$" "$( [[ -n "${IP}" ]] && echo true || echo false )" >>"$TELEM"
```

#### Appendix C — Guard `bin/require-config-root`

```bash
#!/usr/bin/env bash
set -euo pipefail
: "${CONFIG_ROOT:=/config}"
: "${REQUIRE_CONFIG_WRITABLE:=1}"

if [[ ! -d "$CONFIG_ROOT" ]]; then
  echo "[guard] ERROR: $CONFIG_ROOT missing or not a directory" >&2
  exit 2
fi

if [[ "$REQUIRE_CONFIG_WRITABLE" = "1" && ! -w "$CONFIG_ROOT" ]]; then
  echo "[guard] ERROR: $CONFIG_ROOT not writable; set REQUIRE_CONFIG_WRITABLE=0 for RO contexts" >&2
  exit 3
fi

if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY' || true
import os
rp=os.path.realpath("/config")
print(f"[guard] OK: {rp}")
PY
else
  echo "[guard] OK: $CONFIG_ROOT"
fi
```

#### Appendix D — Health `bin/config-health`

```bash
#!/usr/bin/env bash
set -euo pipefail
TARGET="${1:-/config}"
NODE_TYPE="$(stat -f '%HT' "$TARGET" 2>/dev/null || echo 'UNKNOWN')"
REALPATH="$(python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "$TARGET" 2>/dev/null || echo "$TARGET")"
MOUNTED="$(mount | grep -E ' /System/Volumes/Data/homeassistant .*smbfs' >/dev/null && echo true || echo false)"
WRITE_OK=true
touch "$TARGET/.health_write_test" 2>/dev/null || WRITE_OK=false
[[ "$WRITE_OK" = true ]] && rm -f "$TARGET/.health_write_test" 2>/dev/null || true
echo "node_type=$NODE_TYPE"
echo "realpath=$REALPATH"
echo "mounted=$MOUNTED"
echo "write_ok=$WRITE_OK"
```

#### Appendix E — Linter `tools/lint_paths.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
command -v rg >/dev/null 2>&1 || { echo "ripgrep (rg) required" >&2; exit 2; }
PATTERN='\$HOME/|~/hass|/Volumes/|/n/ha|actions-runner/.+?/hass'
EXCLUDES=( '!**/*.md' '!ADR/deprecated/**' '!library/docs/ADR-imports/**' '!**/.git/**' '!**/.venv/**' '!**/node_modules/**' '!**/*.png' '!**/*.jpg' '!**/*.svg' '!**/*.ico' )
if rg -nE "$PATTERN" --hidden "${EXCLUDES[@]}" .; then
  echo 'ERROR: Disallowed path alias detected. Use /config only.' >&2
  exit 1
else
  echo "OK: path lint passed"
fi
```

---

## Apply Plan

```bash
# 1) Place ADR-0029
mkdir -p /config/hestia/library/docs/ADR
cat > /config/hestia/library/docs/ADR/ADR-0029-ops-mount-telemetry-under-canonical-config.md <<'EOF'
# (paste the ADR-0029 content from above)
EOF

# 2) Install LaunchAgent & mount script
mkdir -p "$HOME/bin" "$HOME/Library/LaunchAgents" "$HOME/Library/Logs/Hestia"
cat > "$HOME/bin/ha-mount.sh" <<'EOF'
# (paste Appendix B)
EOF
chmod +x "$HOME/bin/ha-mount.sh"

cat > "$HOME/Library/LaunchAgents/com.hestia.mount.homeassistant.plist" <<'EOF'
# (paste Appendix A)
EOF

launchctl unload "$HOME/Library/LaunchAgents/com.hestia.mount.homeassistant.plist" >/dev/null 2>&1 || true
launchctl load "$HOME/Library/LaunchAgents/com.hestia.mount.homeassistant.plist"

# 3) Install guards and linter
mkdir -p /config/hestia/bin /config/hestia/tools
cat > /config/hestia/bin/require-config-root <<'EOF'
# (paste Appendix C)
EOF
chmod +x /config/hestia/bin/require-config-root
ln -sf /config/hestia/bin/require-config-root /usr/local/bin/require-config-root 2>/dev/null || true

cat > /config/hestia/tools/lint_paths.sh <<'EOF'
# (paste Appendix E)
EOF
chmod +x /config/hestia/tools/lint_paths.sh

# 4) Ensure Data path exists and owned by user
sudo mkdir -p /System/Volumes/Data/homeassistant
sudo chown "$USER":staff /System/Volumes/Data/homeassistant

# 5) Disable Spotlight on mountpoint (idempotent)
mdutil -i off /System/Volumes/Data/homeassistant >/dev/null 2>&1 || true

# 6) Migrate ADR-0022 → deprecated
mkdir -p /config/hestia/library/docs/ADR/deprecated
if [ -f /config/hestia/library/docs/ADR/ADR-0022-hass-mount-keychain-creds-telemetry.md ]; then
  sed -E 's/^status: .*/status: Superseded/; s/^superseded_by:.*/superseded_by: ADR-0029/' \
    /config/hestia/library/docs/ADR/ADR-0022-hass-mount-keychain-creds-telemetry.md \
    > /config/hestia/library/docs/ADR/deprecated/ADR-0022-hass-mount-keychain-creds-telemetry.md || true
fi
```

---

## Validation Suite

```bash
# Binary checks
stat -f '%HT' /config
python3 -c 'import os; print(os.path.realpath("/config"))'
mount | grep -E ' /System/Volumes/Data/homeassistant .*smbfs' || echo "WARN: not mounted yet"

# LaunchAgent status and logs
launchctl list | grep -q com.hestia.mount.homeassistant && echo "agent_loaded=1" || echo "agent_loaded=0"
tail -n 50 "$HOME/Library/Logs/Hestia/ha-mount.out" 2>/dev/null || true
tail -n 50 "$HOME/Library/Logs/Hestia/ha-mount.err" 2>/dev/null || true

# Health & guard
REQUIRE_CONFIG_WRITABLE=0 /config/hestia/bin/require-config-root
/config/hestia/bin/config-health || true

# Linter
/config/hestia/tools/lint_paths.sh

# Telemetry presence
ls -lh "$HOME/Library/Logs/Hestia/" | grep mount_telemetry || echo "no_telemetry_file_yet"
```

---

## Rollback

* Unload agent: `launchctl unload ~/Library/LaunchAgents/com.hestia.mount.homeassistant.plist`
* Remove mount: `diskutil unmount force /System/Volumes/Data/homeassistant`
* Delete files:

  * `rm -f ~/Library/LaunchAgents/com.hestia.mount.homeassistant.plist`
  * `rm -f ~/bin/ha-mount.sh`
  * `rm -f /config/hestia/bin/require-config-root /usr/local/bin/require-config-root`
  * `rm -f /config/hestia/tools/lint_paths.sh`
* Restore ADR-0022 from deprecated if needed.

---

## Risks & Mitigations

* **Credential prompts recur**: Keychain entries or trusted apps missing → rebuild entries for hostname and IP; ensure paths to binaries match system.
* **DNS/mDNS intermittency**: Agent falls back to IP; maintain both Keychain entries.
* **Editor performance on SMB**: Spotlight disabled; watchers tuned in editor settings if necessary.
* **Partial mounts after sleep**: Agent retries on network state change via `KeepAlive.NetworkState`.

---

## Acceptance Criteria

* `/config` resolves to the Data path; SMB mounted on `/System/Volumes/Data/homeassistant`.
* LaunchAgent loaded; telemetry lines written on (re)mount.
* Guard passes in RO mode; linter passes; no disallowed paths.
* ADR-0022 is marked Superseded and archived; ADR-0029 present and governs operations.

END OF DELIVERABLE
```
