---
title: "ADR-0016: Canonical HA edit root & non-interactive SMB mount"
date: 2025‑09‑24
authors: 
  - "Strategos GPT"
  - "Evert Appels"
status: Proposed → Accepted (on merge)
supersedes: Any prior docs or scripts that designate `/n/ha` or `/private/var/ha_real` as the canonical edit root
related:
  - "ADR‑0009 ADR governance & formatting (conformance), HA→Influx telemetry decision, HA→NAS→Git pipeline"
references:
  - "hestia/tools/one_shots/hass_mount_once.sh - idempotent mount helper (LaunchAgent-friendly)"
  - "hestia/tools/one_shots/com.local.hass.mount.plist - sample LaunchAgent plist using KeepAlive.NetworkState"
---

# ADR-0016 — Canonical HA edit root & non‑interactive SMB mount

> Use a per‑user, non‑interactive SMB mount of the Home Assistant Pi share `//<user>@homeassistant.local/config` at `~/hass` (no system daemons, no symlinks). Make `~/hass` the single canonical edit root and normalize HA→NAS→Git and HA→Influx around this root.

## Context
	- HA runtime is on a Raspberry Pi 5. The NAS (DS220+) hosts mirrors and Git bare repos, and optionally exposes additional SMB shares.
	- Historical paths `/n/ha` (autofs) and `/private/var/ha_real` (system LaunchDaemon) caused ownership conflicts, mount races, and editor write failures.
	- VS Code and tooling need a stable, user‑writable path. Home Assistant itself expects `/config` inside the container/OS and should not depend on host‑specific absolute paths.
	- InfluxDB v2 is used as a telemetry backend; HA must reliably write telemetry using a valid token and a reachable backend URL.

## Options considered
  1. Keep autofs `/n/ha` + system LaunchDaemon. This produces conflicts/EX_USAGE on races; root‑owned mounts broke editor writes.
  2. System‑wide mount at `/Volumes/...`. This still runs in a root context; it is brittle and Finder may remap.
  3. Per‑user LaunchAgent mounting to `~/hass` with Keychain auth (Chosen). This produces a user‑owned, idempotent, reliable, and editor‑friendly experience.

## Decision details

	- Canonical edit root (Mac): `~/hass` (absolute `/Users/<user>/hass`).
	- Mount mechanism: LaunchAgent `com.local.hass.mount` (GUI domain) calls an idempotent helper (`hass_mount_once.sh`) that:
		- Checks if the correct share is already mounted at `~/hass` and exits 0 if so.
		- Uses `mount_smbfs` to perform a non-interactive mount (examples below).
		- Logs to `$HOME/Library/Logs/hass-mount.log`.

	Canonical mount example (preferred, tested):

	```bash
	mount_smbfs -N "//${USER}@homeassistant.local/config" "$HOME/hass"
	```

	Optional (tested) extras — use only if verified on your machine:

	```bash
	mount_smbfs -N -d 0777 -f 0777 "//${USER}@homeassistant.local/config" "$HOME/hass"
	```

	Keychain / non-interactive auth (preferred: create interactively; example below shows non-interactive commands and keeps the four-byte SMB protocol code `smb ` with trailing space):

	```bash
	# Delete any existing entry (ignore errors)
	security delete-internet-password -s homeassistant.local -a '<user>' -r 'smb ' >/dev/null 2>&1 || true
	# Add login keychain Internet-password for SMB and allow /sbin/mount_smbfs to access it
	security add-internet-password -s homeassistant.local -a '<user>' -r 'smb ' -T /sbin/mount_smbfs -l ha_haos_login
	# Optional non-interactive (stores secret in history—use with extreme caution):
	# security add-internet-password -s homeassistant.local -a '<user>' -r 'smb ' -w '<password>' -U -T /sbin/mount_smbfs
	```

LaunchAgent plist (example)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
	<dict>
		<key>Label</key>
		<string>com.local.hass.mount</string>
		<key>ProgramArguments</key>
		<array>
			<string>/Users/&lt;user&gt;/bin/hass_mount_once.sh</string>
		</array>
		<key>RunAtLoad</key>
		<true/>
		<key>KeepAlive</key>
		<dict>
			<key>NetworkState</key>
			<true/>
		</dict>
		<key>StandardOutPath</key>
		<string>/Users/&lt;user&gt;/Library/Logs/hass-mount.log</string>
		<key>StandardErrorPath</key>
		<string>/Users/&lt;user&gt;/Library/Logs/hass-mount.log</string>
	</dict>
</plist>
```

## Prohibitions
  - No system LaunchDaemon mount for this share; do not mount to `/private/var/ha_real`.
  - No repo‑embedded symlinks to live system paths; no nested `.git/` directories tracked.
  - HA config paths remain `/config/...` within HA. The host’s `~/hass` is an edit view, not a runtime dependency.
  - Git: The HA config repo root is `~/hass`. `.gitignore` excludes HA runtime noise (`.storage`, DB/logs, `deps`, `.venv`, etc.). A bare repo on NAS must be reachable via SSH as `gituser` and live under a package‑compatible, ACL‑correct path (for example, `/volume1/git-mirrors/ha-config.git`).
  - Influx: HA writes to the Influx backend using a token with read/write on bucket `homeassistant` in org `Hestia`. Default transport is direct `http://<nas>:8086` unless a valid TLS proxy is configured.

## Scope
	- Applies to Mac workstations editing HA config.
	- Does not alter HA’s internal `/config` semantics.
	- Codifies NAS Git hosting and minimal ACLs for SSH push/pull via `gituser`.

## Guardrails (enforced rules)
  1. Single owner of the mount: Only the user LaunchAgent may manage `~/hass`. System daemon mounts for the same share are forbidden.
  2. No symlinks to live paths in the repo; no nested `.git/` shall be tracked.
  3. Keychain‑backed SMB auth (no plain creds in `nsmb.conf`).
  4. Influx token hygiene: `secrets.yaml` must reference a token that can list the `homeassistant` bucket and write a probe.
  5. Hostname strategy: Prefer `homeassistant.local` or the Pi IP consistently. TLS endpoints must have certificates matching the hostname used.

## Canonicalization rules

These rules are authoritative for all editors, scripts, tooling, and documentation in this repository:

1. Internal Home Assistant runtime paths that reference `/config/...` MUST NOT be modified. Those paths live inside the Pi/container and are runtime-facing; the host edit view must not rewrite them.

2. All VS Code workspaces, scripts, and external tooling that currently point at `/n/ha` MUST be updated to use the canonical edit root `~/hass`. For clarity and reproducibility, `~/hass` resolves to `/Users/evertappels/hass` in examples and automated replacements.

3. Path style guidance:
	- When working outside the config workspace (for example, tools run from your $HOME or system scripts), prefer absolute paths: `/Users/evertappels/hass/...`.
	- When working inside the config workspace (for example, the VS Code workspace saved under `~/hass`), prefer relative paths such as `.` or `./packages/my_package` so the workspace is portable and `~/hass` is effectively resolved by using the workspace root.

#### Canonicalization Examples

**A. Absolute** (outside workspace)
```bash
/Users/evertappels/hass/.vscode/hass.code-workspace
```
**B. Relative** (inside workspace saved in ~/hass)

```bash
# .vscode/hass.code-workspace (or folders: [{"path": "."}, ...])
```

## Token Blocks

### Confirmation tokens

Required acks:

`ACK_DISABLE_SYSTEM_DAEMON`=I_UNDERSTAND for any script that unloads/removes com.local.ha.mount.real.
`ACK_AUTOMOUNT_CHANGES`=YES for any script that edits /etc/auto_master or autofs maps.
`ACK_REPO_CLEAN`=NO_SYMLINKS_NO_NESTED_GIT before initial push.

Scripts below will refuse to proceed without these environment variables.

Enforcement (scripts should hard-fail if these are not set):

```
: "${ACK_DISABLE_SYSTEM_DAEMON:?set ACK_DISABLE_SYSTEM_DAEMON=I_UNDERSTAND}"
: "${ACK_AUTOMOUNT_CHANGES:?set ACK_AUTOMOUNT_CHANGES=YES}"
: "${ACK_REPO_CLEAN:?set ACK_REPO_CLEAN=NO_SYMLINKS_NO_NESTED_GIT}"
```

### Programmatic validation

### A. Mount health & ownership

```bash
MNT="$HOME/hass"
set -e
[ -d "$MNT" ] || { echo "FAIL: missing $MNT"; exit 1; }
mount | grep -qE " on $MNT \(smbfs" || { echo "FAIL: not mounted"; exit 2; }
SRC=$(mount | awk -v m="$MNT" '$0 ~ " on " m " \\(" {print $1; exit}')
case "$SRC" in
	//*@homeassistant*/config|//*@[0-9]*.[0-9]*.[0-9]*.[0-9]*/config) echo "OK: source=$SRC";;
	*) echo "FAIL: wrong source: $SRC"; exit 3;;
esac
# write probe
( date > "$MNT/.ha_write_test" && rm -f "$MNT/.ha_write_test" ) && echo "WRITE_OK" || { echo "WRITE_FAIL"; exit 4; }
```


#### B. LaunchAgent sanity

```bash
launchctl list | grep -q com.local.hass.mount && echo AGENT_LOADED || echo AGENT_NOT_LOADED
launchctl print "gui/$(id -u)/com.local.hass.mount" 2>/dev/null | egrep 'state|last exit code' || true
```

#### C. Ban system daemon competition (requires ACK)

```bash
: "${ACK_DISABLE_SYSTEM_DAEMON:?set ACK_DISABLE_SYSTEM_DAEMON=I_UNDERSTAND}"
sudo launchctl list 2>/dev/null | grep -q com.local.ha.mount.real && {
	sudo launchctl bootout system/com.local.ha.mount.real || true
	sudo launchctl disable system/com.local.ha.mount.real || true
	echo "System daemon disabled"
} || echo "System daemon not loaded"
```

#### D. Repo hygiene (run in `~/hass`)

```bash
cd "$HOME/hass"
# symlinks that would be tracked
BAD=$(find . -type l -print | while read -r f; do git check-ignore -q "$f" || echo "$f"; done)
[ -z "$BAD" ] && echo "SYMLINKS_OK" || { echo "FAIL: symlinks tracked:\n$BAD"; exit 10; }
# nested .git directories
NEST=$(find . -type d -name .git -not -path './.git')
[ -z "$NEST" ] && echo "NESTED_GIT_OK" || { echo "FAIL: nested .git:\n$NEST"; exit 11; }
# large staged files (>50MB)
BIG=$(git diff --cached --name-only --diff-filter=AM | while read -r f; do [ -f "$f" ] || continue; s=$(wc -c < "$f"); [ "$s" -gt 52428800 ] && echo "$f ($s bytes)"; done)
[ -z "$BIG" ] && echo "SIZE_OK" || { echo "FAIL: large files staged:\n$BIG"; exit 12; }
```

#### E. Influx acceptance (run on HA host or from a node that can reach the NAS)

```bash
URL="http://192.168.0.104:8086"; ORG="Hestia"; BUCKET="homeassistant"
: "${INFLUX_TOKEN:?export INFLUX_TOKEN=<rw-token>}"
# list buckets
curl -fsS -H "Authorization: Token $INFLUX_TOKEN" "$URL/api/v2/buckets?org=$ORG" >/dev/null && echo BUCKETS_OK || { echo BUCKETS_FAIL; exit 20; }
# write probe with server timestamp
curl -fsS -XPOST -H "Authorization: Token $INFLUX_TOKEN" "$URL/api/v2/write?org=$ORG&bucket=$BUCKET" \
	--data-binary 'ha_probe,host=ha value=1i' >/dev/null && echo WRITE_OK || { echo WRITE_FAIL; exit 21; }
# query probe (JSON)
QR=$(curl -fsS -XPOST -H "Authorization: Token $INFLUX_TOKEN" -H 'Accept: application/csv' \
	"$URL/api/v2/query?org=$ORG" --data '{"query":"from(bucket:\"homeassistant\") |> range(start: -15m) |> filter(fn: (r) => r._measurement == \"ha_probe\") |> last()"}') && echo QUERY_OK || echo QUERY_FAIL
```

#### F. NAS / Git acceptance (developer workstation)

```
# Workstation check
git ls-remote ssh://gituser@192.168.0.104/volume1/git-mirrors/ha-config.git

# If it fails, on NAS as root ensure ACLs and parent dirs are traversable by gituser:
chown -R gituser:users /volume1/git-mirrors/ha-config.git
chmod -R g+ws /volume1/git-mirrors/ha-config.git
chmod g+rx /volume1 /volume1/git-mirrors
# Retry ls-remote from workstation
```

Note: Some Synology Git packages expose repositories only from package-managed roots. If arbitrary paths under `/volume1` fail, create the bare repo under the package's managed repo directory or ensure the package is configured to include `/volume1/git-mirrors`.

### Migration plan
	1.	Install LaunchAgent helper into user home; ensure Keychain entry exists.
	2.	Unload/disable any system daemon mounts for this share (require ACK_DISABLE_SYSTEM_DAEMON).
	3.	Update tooling to use ~/hass (VS Code workspace, scripts). Replace /n/ha string refs.
	4.	Git: initialize in ~/hass, apply .gitignore, push to NAS bare repo. Ensure NAS ACLs allow gituser to traverse /volume1/git-mirrors and read/write the repo.
	5.	Influx: validate token and bucket access; confirm HA writes succeed (acceptance checks).

#### Backout
	•	If necessary, revert VS Code workspace and re‑enable autofs /n/ha. Risks: re‑introduces mount races and write failures; not recommended.

#### Edge cases & mitigations
	•	Automount collision (Finder or autofs mounted same share elsewhere): helper is idempotent and exits 0 when correct mount exists; logs a warning if a different share occupies ~/hass.
	•	Keychain item missing → interactive prompt: create Login Keychain Internet‑password for homeassistant.local with protocol smb .
	•	TLS hostname mismatch (Influx via Synology RP): pin URL to http://<nas>:8086 until reverse‑proxy routes /api/v2/* and cert CN matches the hostname used.
	•	NAS ACL denies SSH git: ensure gituser can execute (x) each parent dir and R/W repo dir; on Synology use synoacltool or POSIX chmod/chown as documented.

#### Governance review (ADR‑0009)
**Formatting**: This ADR follows numbered header, status, context/decision/consequences, and includes validation & rollback sections per ADR‑0009.
**Conflicts**: None with governance/formatting. This ADR supersedes any prior guidance naming /n/ha or /private/var/ha_real as canonical edit roots. If an earlier ADR mandated those paths, this ADR deprecates them and establishes ~/hass as authoritative on Mac.

#### Consequences

**Positive**
	•	Stable, user‑writable mount; editors and CLI tools operate without sudo or ownership issues.
	•	Reduced drift: one canonical edit root; repo ignores runtime noise; HA telemetry validated.

**Negative / costs**
	•	macOS‑specific LaunchAgent requires per‑user setup.
	•	Autofs references to /n/ha must be cleaned up to avoid confusion.

### Acceptance criteria (must all PASS)
	•	`MOUNT_OK` and `WRITE_OK` from section A.
	•	AGENT_LOADED with non‑error last exit from section B.
	•	SYSTEM_DAEMON not loaded from section C.
	•	Repo checks SYMLINKS_OK, NESTED_GIT_OK, SIZE_OK from section D.
	•	BUCKETS_OK, WRITE_OK, and a non‑empty query result from section E.

	•	GIT_OK: `git ls-remote` against the NAS bare repo succeeds from a developer host (and any required ACL fixes applied on NAS).

### Operational runbook snippets
	•	Reload agent: `launchctl unload -w ~/Library/LaunchAgents/com.local.hass.mount.plist && launchctl load -w ~/Library/LaunchAgents/com.local.hass.mount.plist`
	•	View logs: `tail -n 120 ~/Library/Logs/hass-mount.log`
	•	Fix NAS git ACL quickly (example):

```bash
sudo chown -R gituser:users /volume1/git-mirrors/ha-config.git
sudo chmod -R g+ws /volume1/git-mirrors/ha-config.git
sudo chmod g+rx /volume1 /volume1/git-mirrors
# or synoacltool additions as needed
```

### Changelog
	•	2025‑09‑24: Initial decision drafted; defines ~/hass as canonical edit root; adds guardrails & validation.