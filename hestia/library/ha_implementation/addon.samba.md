---
title: "Home Assistant Add-on: Samba share"
authors: "Home Assistant"
source: "Home Assistant Docs"
slug: "addon-samba"
tags: ["home-assistant","addon","samba","ops"]
original_date: "2022-04-05"
last_updated: "2025-10-03"
url: "https://www.home-assistant.io/addons/samba/"
---

# Home Assistant Add-on: Samba Share

> Network file sharing add-on that allows you to access your Home Assistant configuration and files over SMB/CIFS protocol from Windows, macOS, and Linux systems.

## Internal References

- **Configuration Files**: Access via Samba share at `//HA_IP/config`
- **Backup Management**: Access backups via `//HA_IP/backup` 
- **Add-on Configuration**: Access add-on configs via `//HA_IP/addon_configs`
- **Related Components**: `recorder`, `backup`, `file_editor`
- **Security**: Network access controls and authentication
## Installation

Follow these steps to get the add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Settings** → **Add-ons** → **Add-on store**
2. Find the "Samba share" add-on and click it
3. Click on the **INSTALL** button
## How to Use

1. **Set Credentials**: In the configuration section, set a username and password. You can specify any username and password; these are not related in any way to the login credentials you use to log in to Home Assistant or to log in to the computer with which you will use Samba share
2. **Configure Shares**: Review the enabled shares. Disable any you do not plan to use. Shares can be re-enabled later if needed
## Connection

### Access Paths

- **Windows**: `\\<IP_ADDRESS>\`
- **macOS**: `smb://<IP_ADDRESS>`
- **Linux**: `smb://<IP_ADDRESS>` or mount via `/etc/fstab`

### Available Shares

This add-on exposes the following directories over SMB (Samba):

| Directory | Description |
|-----------|-------------|
| `addons` | This is for your local add-ons |
| `addon_configs` | This is for the configuration files of your add-ons |
| `backup` | This is for your backups |
| `config` | This is for your Home Assistant configuration |
| `media` | This is for local media files |
| `share` | This is for your data that is shared between add-ons and Home Assistant |
| `ssl` | This is for your SSL certificates |
## Configuration

### Example Configuration

```yaml
workgroup: WORKGROUP
local_master: true
username: homeassistant
password: YOUR_PASSWORD
enabled_shares:
  - addons
  - addon_configs
  - backup
  - config
  - media
  - share
  - ssl
allow_hosts:
  - 10.0.0.0/8
  - 172.16.0.0/12
  - 192.168.0.0/16
  - 169.254.0.0/16
  - fe80::/10
  - fc00::/7
veto_files:
  - "._*"
  - ".DS_Store"
  - Thumbs.db
compatibility_mode: false
```
### Configuration Options

#### Required Options

- **`workgroup`** (required) - Change `WORKGROUP` to reflect your network needs
- **`local_master`** (required) - Enable to try and become a local master browser on a subnet
- **`username`** (required) - The username you would like to use to authenticate with the Samba server
- **`password`** (required) - The password that goes with the username configured for authentication
- **`enabled_shares`** (required) - List of Samba shares that will be accessible. Any shares removed or commented out of the list will not be accessible
- **`allow_hosts`** (required) - List of hosts/networks allowed to access the shared folders

#### Optional Options

- **`veto_files`** (optional) - List of files that are neither visible nor accessible. Useful to stop clients from littering the share with temporary hidden files (e.g., macOS `.DS_Store` or Windows `Thumbs.db` files)
- **`compatibility_mode`** (optional, default: `false`) - Setting this option to `true` will enable old legacy Samba protocols on the Samba add-on. This might solve issues with some clients that cannot handle the newer protocols, however, it lowers security. Only use this when you absolutely need it and understand the possible consequences
- **`apple_compatibility_mode`** (optional, default: `true`) - Enable Samba configurations to improve interoperability with Apple devices. This can cause issues with file systems that do not support xattr such as exFAT

## Support

Got questions? You have several options to get them answered:

- [Home Assistant Discord Chat Server](https://discord.gg/home-assistant)
- [Home Assistant Community Forum](https://community.home-assistant.io/)
- [Reddit subreddit /r/homeassistant](https://reddit.com/r/homeassistant)
- [GitHub Issues](https://github.com/home-assistant/addons/issues) - For bug reports

## Security Considerations

- Always use strong, unique passwords for Samba authentication
- Restrict `allow_hosts` to your local network ranges only
- Regularly review enabled shares and disable unused ones
- Consider using `veto_files` to prevent system file pollution
- Monitor access logs for unauthorized access attempts