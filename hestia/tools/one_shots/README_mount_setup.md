# macOS ~/hass SMB Mount Setup

This directory contains the idempotent mount helper and LaunchAgent plist for mounting the Home Assistant config share at `~/hass` per ADR-0016.

## Files

- `hass_mount_once.sh` - Idempotent helper script that mounts `//user@homeassistant.local/config` at `~/hass`
- `com.local.hass.mount.plist` - Sample LaunchAgent plist for automatic mounting with network state monitoring

## Installation Steps

### 1. Add Keychain Entry (Interactive - Recommended)

```bash
# Add keychain entry and allow mount_smbfs to access it
security add-internet-password -s homeassistant.local -a '<your-username>' -r 'smb ' -T /sbin/mount_smbfs -l ha_haos_login
```

Replace `<your-username>` with your actual Home Assistant username. This will prompt for the password interactively.

### 2. Test the Helper Script

First, test the helper manually:

```bash
# Set environment variables
export SMB_USER="<your-username>"
export SMB_HOST="homeassistant.local" 
export SMB_SHARE="config"

# Test the mount (this is idempotent)
cd ~/hass/hestia/tools/one_shots
bash hass_mount_once.sh
```

### 3. Install LaunchAgent (Optional)

For automatic mounting on network state changes:

```bash
# Copy plist to user LaunchAgents
cp ~/hass/hestia/tools/one_shots/com.local.hass.mount.plist ~/Library/LaunchAgents/

# Load and enable the agent
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.local.hass.mount.plist
launchctl enable gui/$(id -u)/com.local.hass.mount
```

## Verification

Check mount status:
```bash
mount | grep -E " on $HOME/hass \\(smbfs"
```

Check LaunchAgent status:
```bash
launchctl list | grep com.local.hass.mount
launchctl print "gui/$(id -u)/com.local.hass.mount"
```

Check logs:
```bash
tail -f ~/Library/Logs/hass-mount.log
```

## Troubleshooting

- **Keychain access denied**: Re-run the `security add-internet-password` command and ensure `/sbin/mount_smbfs` is in the trusted applications list
- **Permission denied**: Ensure the helper script is executable: `chmod +x hass_mount_once.sh`
- **Mount fails**: Check network connectivity to `homeassistant.local` and verify credentials
- **LaunchAgent not starting**: Check Console.app for system errors, ensure plist syntax is valid

## Related ADRs

- ADR-0016: Canonical HA edit root & non-interactive SMB mount
- ADR-0017: Fallback local logging path for HA tooling

## Security Notes

- Keychain entries are stored securely in the macOS login keychain
- The LaunchAgent runs in user context (not system/root)
- Logs are written to `~/Library/Logs/hass-mount.log` with user-only permissions