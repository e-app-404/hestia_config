# Hestia / Home Assistant — macOS SMB mount cutover & git remote normalization

## Final review — facts & corrections

* **Root cause of the “Usage: add-internet-password …” loop (certain):** we passed `-k` to `security add-internet-password`. That flag doesn’t exist; the keychain path must be the **positional last argument**. Result: **System.keychain** never got the SMB credential; every root mount hit `Authentication error`.
* **Mount succeeded once but writes failed (certain):** share permissions (or veto) blocked writes. Local `-f/-d` mount flags do **not** override server ACLs/veto; you must use a share with RW and dotfiles allowed (e.g., `HA_MIRROR` or `git`) or fix DSM ACL/veto.
* **Protocol code (certain):** SMB protocol is **`'smb '`** (four chars incl. trailing space) in keychain ops.
* **Scope guard (certain):** no autofs changes; non-`/Volumes` mountpoint is `/private/var/ha_real`.
* **HA↔Influx (not priority today):** your YAMLs are correct in the canvas; diag path should be `/config/diag` (not `/config/hestia/diag`). We will not touch HA until the mount is stable.
* **Git (certain):** you have mixed remotes. We’ll standardize to DSM (`ds220plus.reverse-beta.ts.net`) and keep GitHub as a secondary remote where applicable.

---

## 1) SMB mount cutover — one deterministic block (prompts: macOS admin + NAS password)

This creates the **System.keychain** item correctly (positional keychain arg), mounts the **`HA_MIRROR`** share first (then falls back to `home`, `git`, `hestia` if needed), and verifies a write with a non-dot file.

```bash
PASS=$(security find-internet-password -s 192.168.0.104 -a babylonrobot -r 'smb ' -g 2>&1 | awk -F\" '/password:/ {print $2}'); [ -n "$PASS" ] || { read -s -p "NAS (Synology) password for SMB user '\''babylonrobot'\'': " PASS; echo; }
[ -n "$PASS" ] || { echo "ABORT: empty NAS password"; exit 70; }
sudo -p "[macOS admin password for evertappels] " /bin/bash -lc '
set -euo pipefail
SERVER=192.168.0.104
USER=babylonrobot
MP=/private/var/ha_real
KEYCHAIN=/Library/Keychains/System.keychain
PW="'"$PASS"'"
security delete-internet-password -s "$SERVER" -a "$USER" -r "smb " "$KEYCHAIN" 2>/dev/null || true
security add-internet-password -a "$USER" -s "$SERVER" -r "smb " -T /sbin/mount_smbfs -T /usr/libexec/automountd -l ha_nas_system -w "$PW" "$KEYCHAIN"
security find-internet-password -s "$SERVER" -a "$USER" -r "smb " "$KEYCHAIN" >/dev/null
umount -f "$MP" 2>/dev/null || true
install -d -o root -g wheel -m 755 "$MP"
mounted=0
for share in HA_MIRROR home git hestia; do
  mount_smbfs -N "//$USER@$SERVER/$share" "$MP" || mount_smbfs -N "//WORKGROUP;$USER@$SERVER/$share" "$MP" || true
  if mount | grep -q " $MP "; then echo "$share" > "$MP/.share_used.txt" 2>/dev/null || true; mounted=1; break; fi
done
[ "$mounted" -eq 1 ] || { echo "MOUNT_FAILED"; exit 65; }
sudo -u evertappels /bin/bash -lc "echo ok > \"$MP/probe.txt\"" || { echo "WRITE_FAILED"; exit 66; }
mount | grep " $MP "
'
```

**Prompts you will see**

1. `[macOS admin password for evertappels]` → local sudo.
2. `NAS (Synology) password for SMB user 'babylonrobot':` → stored into **System.keychain** for non-interactive mounts.

**Result interpretation**

* Prints the mounted line (e.g., `… /HA_MIRROR on /private/var/ha_real …`) and creates `probe.txt` → **good**.
* `MOUNT_FAILED` → server refused connection; recheck creds/host.
* `WRITE_FAILED` → mount is OK but share is read-only or vetoes writes/dotfiles. Use a different share (e.g., `git`) or fix DSM permissions/veto, then rerun the block.

---

## 2) Persistence (after 1 succeeds; uses the share actually mounted)

If 1 mounted `HA_MIRROR`, use as-is. If it mounted another, adjust `SRC` accordingly before running.

```bash
SRC="//babylonrobot@192.168.0.104/$(cat /private/var/ha_real/.share_used.txt 2>/dev/null || echo HA_MIRROR)"
sudo /bin/bash -lc '
set -euo pipefail
MP=/private/var/ha_real
cat >/usr/local/sbin/ha_mount_helper <<SH
#!/usr/bin/env bash
set -euo pipefail
MP="$MP"; SRC="'"$SRC"'"; LOG="/var/log/ha-mount.log"
exec >>"\$LOG" 2>&1
echo "==== \$(date -Iseconds) start"
mount | grep -q " \$MP " || { mkdir -p "\$MP"; /sbin/mount_smbfs -N "\$SRC" "\$MP"; }
mount | grep -q " \$MP " || exit 64
SH
install -o root -g wheel -m 755 /usr/local/sbin/ha_mount_helper
cat >/Library/LaunchDaemons/com.local.ha.mount.real.plist <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.local.ha.mount.real</string>
  <key>ProgramArguments</key><array><string>/usr/local/sbin/ha_mount_helper</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>NetworkState</key><true/></dict>
  <key>StandardOutPath</key><string>/var/log/ha-mount.log</string>
  <key>StandardErrorPath</key><string>/var/log/ha-mount.log</string>
</dict></plist>
PLIST
chown root:wheel /Library/LaunchDaemons/com.local.ha.mount.real.plist
chmod 644 /Library/LaunchDaemons/com.local.ha.mount.real.plist
launchctl bootstrap system /Library/LaunchDaemons/com.local.ha.mount.real.plist 2>/dev/null || launchctl bootstrap system /Library/LaunchDaemons/com.local.ha.mount.real.plist
launchctl enable system/com.local.ha.mount.real
launchctl kickstart -k system/com.local.ha.mount.real
sleep 1; mount | grep " $MP "
'
```

---

## 3) Git remote normalization (two repos)

**Assumptions (explicit):**

* Canonical DSM host: `ds220plus.reverse-beta.ts.net`.
* Canonical DSM git user: `gituser`.
* Paths: `/volume1/git/…` and `/volume1/git-mirrors/…` as in your outputs.

### 3.1 `omega_registry` (run inside that repo)

```bash
HOST=ds220plus.reverse-beta.ts.net
NASUSER=gituser
git remote set-url origin "ssh://$NASUSER@$HOST/volume1/git/omega_registry.git"
git remote set-url --add --push origin "ssh://$NASUSER@$HOST/volume1/git/omega_registry.git"
git remote set-url --push --add origin "https://github.com/e-app-404/omega_registry.git"
git remote set-url --add github "https://github.com/e-app-404/omega_registry.git" 2>/dev/null || git remote add github "https://github.com/e-app-404/omega_registry.git"
git remote -v
```

### 3.2 `HA-BB8` (run inside that repo)

```bash
HOST=ds220plus.reverse-beta.ts.net
NASUSER=gituser
git remote set-url origin "ssh://$NASUSER@$HOST/volume1/git-mirrors/ha-config.git"
git remote set-url --add --push origin "ssh://$NASUSER@$HOST/volume1/git-mirrors/ha-config.git"
git remote -v
```

> If your authoritative DSM SSH user or host differs (e.g., `babylonrobot@dsm-git-host`), replace `NASUSER`/`HOST` accordingly.

---

## Acceptance (binary)

* `mount | grep ' /private/var/ha_real '` shows a mounted share **and** `cat /private/var/ha_real/probe.txt` returns `ok`.
* After reboot or network flap: the mount is back (daemon does it).
* `git remote -v` in both repos shows normalized remotes as above.

If any of the three blocks fails, paste the **last 10 lines** of output from that block only, and I’ll return a single corrected block.
