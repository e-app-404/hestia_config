# Strategos Takeover Kit — HA ↔ Influx + macOS SMB (non-/Volumes)

**Objective:** Restore a reliable, non-interactive SMB mount for the Home Assistant Git workspace on macOS (non-/Volumes, keychain-backed) and prove live HA→Influx writes. Non-destructive by default; **no autofs edits**.

---

## 0) Quick Acceptance Checklist (binary)

* [ ] `/private/var/ha_real` mounted and writable by `evertappels`.
* [ ] LaunchDaemon keeps mount alive across network changes/reboots.
* [ ] HA logs include `homeassistant.components.influxdb` debug lines.
* [ ] Influx shows recent HA measurements after restart and interaction.

---

## 1) Fixes — HA config (two high-likelihood root causes)

### 1.1 `packages/integrations/influxdb.yaml` (correct structure)

> **Replace** contents with this minimal, valid v2 block (note the `influxdb:` root key and `token`, not `token_secret_ref`).

```yaml
influxdb:
  api_version: 2
  host: 192.168.0.104
  port: 8086
  token: !secret influxdb_token
  organization: Hestia
  bucket: homeassistant
  # Optional tuning (keep commented until validated)
  # max_retries: 3
  # default_measurement: state
  # tags:
  #   source: homeassistant
  # include:
  #   entities: []
  # exclude:
  #   domains: []
```

### 1.2 `packages/integrations/logger.yaml` (mapping, not list)

> **Replace** list-of-strings with a mapping to enable component-level debug.

```yaml
logger:
  default: info
  logs:
    homeassistant.components.influxdb: debug
    influxdb_client.client.write: debug
    influxdb_client.client.influxdb_client: debug
```

### 1.3 Sanity: `configuration.yaml`

Confirm it contains:

```yaml
packages: !include_dir_named packages
```

---

## 2) Diagnostics — HA ↔ Influx evidence pack

Create `/config/hestia/diag` if missing and run the script below on the HA host.

Run these quick preflight checks inside the SSH add-on before executing the script. Prefer exporting `INFLUX_TOKEN` manually in your session rather than relying on automatic extraction.

```bash
if command -v ha >/dev/null 2>&1; then echo "ha: available"; else echo "ha: not available (core checks will be skipped)"; fi
curl -sS http://192.168.0.104:8086/health | sed -n '1,5p'
mkdir -p /config/hestia/diag && test -w /config/hestia/diag && echo "/config/hestia/diag writable" || echo "/config/hestia/diag not writable"
curl -s -H "Authorization: Token $INFLUX_TOKEN" "http://192.168.0.104:8086/api/v2/health" | grep -q '"status":"pass"' && echo "Influx token OK" || echo "Influx token invalid or request failed"
```

### 2.1 `ha_influx_diag.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
OUT=/config/hestia/diag
mkdir -p "$OUT"
log() { printf '%s %s\n' "$(date -Iseconds)" "$*" | tee -a "$OUT/diag.log"; }

log "[1/5] Influx /health"
curl -s http://192.168.0.104:8086/health | tee "$OUT/influx_health.txt" >/dev/null

log "[2/5] Smoke write"
: "${INFLUX_TOKEN:?export INFLUX_TOKEN before running}"
TS=$(date +%s%N)
echo "ha_smoketest,host=nas value=1i $TS" | tee "$OUT/influx_write_head.txt" >/dev/null
curl -s -i -X POST 'http://192.168.0.104:8086/api/v2/write?org=Hestia&bucket=homeassistant&precision=ns' \
  -H "Authorization: Token $INFLUX_TOKEN" --data-binary @"$OUT/influx_write_head.txt" | tee "$OUT/influx_write_rc.txt" >/dev/null

log "[3/5] Flux query"
cat >"$OUT/q.json" <<'JSON'
{"query":"from(bucket:\"homeassistant\") |> range(start:-5m) |> filter(fn:(r)=>r._measurement==\"ha_smoketest\") |> last()"}
JSON
curl -s 'http://192.168.0.104:8086/api/v2/query?org=Hestia' -H "Authorization: Token $INFLUX_TOKEN" -H 'Content-Type: application/json' -d @"$OUT/q.json" | tee "$OUT/influx_query.txt" >/dev/null

log "[4/5] HA core check/logs"
ha core check | tee "$OUT/ha_core_check.txt" || true
ha core logs --no-color | tee "$OUT/ha_core_full.log" >/dev/null || true

grep -i -E 'influxdb|influxdb_client' "$OUT/ha_core_full.log" | tail -n 200 | tee "$OUT/ha_influx_tail.log" >/dev/null || true

log "[5/5] Summary"
python3 - <<'PY'
import json, os, re
p = '/config/hestia/diag'
health = open(os.path.join(p,'influx_health.txt')).read()
q = open(os.path.join(p,'influx_query.txt')).read()
rc = open(os.path.join(p,'influx_write_rc.txt')).read()
s = {
  'health_pass': '"status":"pass"' in health,
  'write_204': ' 204' in rc.splitlines()[0] if rc else False,
  'query_found_last': 'ha_smoketest' in q,
}
print(json.dumps(s, indent=2))
PY
```

---

## 3) macOS — Stable non-/Volumes mount

### 3.1 Keychain (verify then add if missing) — **no passwords in CLI args**

```bash
# Verify
security find-internet-password -s 192.168.0.104 -a babylonrobot -r 'smb ' -g
sudo security find-internet-password -s 192.168.0.104 -a babylonrobot -r 'smb ' -g /Library/Keychains/System.keychain || true
```

```bash
# Add (you will be prompted). Protocol must be exactly 'smb'
security add-internet-password -a babylonrobot -s 192.168.0.104 -r 'smb ' -U -T /sbin/mount_smbfs -l ha_nas_login
sudo security add-internet-password -a babylonrobot -s 192.168.0.104 -r 'smb ' -U -T /sbin/mount_smbfs -k /Library/Keychains/System.keychain -l ha_nas_system
```

### 3.2 One-shot clean mount (root) — **non-/Volumes** target

```bash
sudo umount -f /private/var/ha_real 2>/dev/null || true
sudo rm -rf /private/var/ha_real
sudo install -d -o root -g wheel -m 755 /private/var/ha_real
sudo mount_smbfs -N "//babylonrobot@192.168.0.104/home" "/private/var/ha_real"
mount | grep ' /private/var/ha_real ' -n || { echo 'MOUNT FAILED' >&2; exit 64; }
sudo -u evertappels sh -c 'touch /private/var/ha_real/.probe && rm -f /private/var/ha_real/.probe'
```

If it still prompts for a password or auth fails, re-write the existing keychain items with trust for `/sbin/mount_smbfs` and (optionally) `/usr/libexec/automountd`, using `-U` and `-w` (so it actually updates the item and ACL):

```bash
security add-internet-password -a babylonrobot -s 192.168.0.104 -r 'smb ' -U \
  -T /sbin/mount_smbfs -T /usr/libexec/automountd -l ha_nas_login -w

sudo security add-internet-password -a babylonrobot -s 192.168.0.104 -r 'smb ' -U \
  -T /sbin/mount_smbfs -T /usr/libexec/automountd -k /Library/Keychains/System.keychain \
  -l ha_nas_system -w
```

Then re-run the mount command above.


### 3.3 Helper script `/usr/local/sbin/ha_mount_helper`

```bash
#!/usr/bin/env bash
set -euo pipefail
MP="/private/var/ha_real"
SRC="//babylonrobot@192.168.0.104/home"
LOG="/var/log/ha-mount.log"
exec >>"$LOG" 2>&1
printf '\n==== %s start ====' "$(date -Iseconds)"; echo

is_mounted(){ mount | grep -q " $MP "; }
prepare(){
  umount -f "$MP" 2>/dev/null || true
  mkdir -p "$MP"
}

attempt(){
  if is_mounted; then echo "already mounted"; return 0; fi
  /sbin/mount_smbfs -N "$SRC" "$MP"
}

prepare
if ! attempt; then
  echo "first attempt failed; cleaning and retrying"
  sleep 1
  umount -f "$MP" 2>/dev/null || true
  rmdir "$MP" 2>/dev/null || true
  mkdir -p "$MP"
  attempt
fi

is_mounted && echo "mounted OK at $MP" || { echo "failed"; exit 64; }
chown -R evertappels:staff "$MP" 2>/dev/null || true
```

```bash
# Install & permissions
sudo install -o root -g wheel -m 755 /tmp/ha_mount_helper /usr/local/sbin/ha_mount_helper
```

### 3.4 LaunchDaemon `/Library/LaunchDaemons/com.local.ha.mount.real.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key><string>com.local.ha.mount.real</string>
    <key>ProgramArguments</key>
    <array>
      <string>/usr/local/sbin/ha_mount_helper</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key>
    <dict>
      <key>NetworkState</key><true/>
    </dict>
    <key>StandardOutPath</key><string>/var/log/ha-mount.log</string>
    <key>StandardErrorPath</key><string>/var/log/ha-mount.log</string>
  </dict>
</plist>
```

```bash
# Load & start
sudo launchctl bootstrap system /Library/LaunchDaemons/com.local.ha.mount.real.plist
sudo launchctl enable system/com.local.ha.mount.real
sudo launchctl kickstart -k system/com.local.ha.mount.real
# Verify
sleep 2; mount | grep ' /private/var/ha_real ' -n
```

---

## 4) Post-fix validation (commands)

### 4.1 HA logging visibility

```bash
ha core restart; sleep 12
ha core logs | grep -i -E 'influxdb|influxdb_client' -n | tail -n 200
```

### 4.2 Generate data and verify in Influx

```bash
# Trigger a few entity state changes (UI or service calls), then:
cat >/tmp/q.json <<'JSON'
{"query":"from(bucket:\"homeassistant\") |> range(start:-5m) |> keep(columns:[\"_time\",\"_measurement\",\"_field\",\"_value\",\"entity_id\"]) |> sort(columns:[\"_time\"], desc:true) |> limit(n:40)"}
JSON
curl -s "http://192.168.0.104:8086/api/v2/query?org=Hestia" -H "Authorization: Token $INFLUX_TOKEN" -H "Content-Type: application/json" -d @/tmp/q.json | sed -n '1,150p'
```

---

## 5) Rollback & Guards

* Revert `logger` to `default: info` once verified.
* Delete only `/config/hestia/diag/*` artifacts if noise is a concern.
* **Do not** alter autofs files unless explicitly authorized.

---

## 6) Evidence-driven Wrap-up

When the steps pass, archive `/config/hestia/diag` plus:

* `mount` output, `launchctl print system/com.local.ha.mount.real`, `/var/log/ha-mount.log`
* Flux query snippet with recent HA measurements.

This completes the binary acceptance for mount stability and HA→Influx observability.
