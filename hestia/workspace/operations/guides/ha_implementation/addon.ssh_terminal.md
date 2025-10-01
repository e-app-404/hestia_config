---
title: "Home Assistant Community Add-on: Advanced SSH & Web Terminal"
authors: "Franck Nijhof, Home Assistant Community Add-ons"
source: "Home Assistant Community Add-ons"
slug: "ha-advanced-ssh-web-terminal"
tags: ["home-assistant", "ssh", "terminal", "add-on", "security", "cli", "web-terminal"]
original_date: "2017-01-01"
last_updated: "2025-10-01"
url: "https://github.com/hassio-addons/addon-ssh"
config_schema:
  log_level: "info|debug|trace|warning|error|fatal"
  ssh:
    username: "string"
    password: "string"
    authorized_keys: "array"
    sftp: "boolean"
    compatibility_mode: "boolean"
    allow_agent_forwarding: "boolean"
    allow_remote_port_forwarding: "boolean"
    allow_tcp_forwarding: "boolean"
  zsh: "boolean"
  share_sessions: "boolean"
  packages: "array"
  init_commands: "array"
---

# Home Assistant Community Add-on: Advanced SSH & Web Terminal

SSH and Web Terminal access to Home Assistant with enhanced security, flexibility, and system-level privileges.

⚠️ **HIGH PRIVILEGE ACCESS**: Full system access including hardware, Docker, and network-level operations.

## Quick Start

```bash
# Install via Home Assistant Add-on Store
# Configure username and SSH keys
# Start add-on
```

## Features

### Core Capabilities
- **OpenSSH Server**: Secure remote access
- **Web Terminal**: Browser-based terminal in HA frontend
- **Mosh Support**: Roaming/intermittent connectivity
- **SFTP**: Optional file transfer (requires `root` user)

### Security
- Secure ciphers and algorithms only
- Brute-force protection
- Configurable user authentication
- SSH key authentication (recommended)
- Optional legacy client compatibility

### System Access
- **Hardware**: Audio, UART/serial, GPIO pins
- **Network**: Host-level networking, port opening
- **Docker**: Container management access
- **D-Bus**: System bus integration
- **Privileges**: Elevated debugging capabilities

### Shell Environment
- **Default**: ZSH with Oh My Zsh
- **Alternative**: Bash fallback
- **Persistence**: Settings/keys preserved across restarts
- **Customization**: Package installation + init commands
- **Session Sharing**: Web ↔ SSH session continuity

### Built-in Tools
```bash
# Network
curl wget rsync nmap

# Development  
git nano vim tmux

# Database
mariadb-client mysql-client

# System
mosquitto-clients wake-on-lan
```

## Installation

1. **Add-on Store** → Advanced SSH & Web Terminal → Install
2. **Configure** authentication (`username` + `authorized_keys`)
3. **Start** add-on
4. **Verify** logs for successful startup

## Configuration

> ⚠️ **Restart required** after configuration changes

### Complete Configuration Schema

```yaml
# Logging
log_level: info  # trace|debug|info|warning|error|fatal

# SSH Settings
ssh:
  username: homeassistant        # string (lowercase)
  password: ""                   # string (empty = disabled, recommended)
  authorized_keys:               # array (recommended)
    - ssh-ed25519 AAAA...        # public key string
    - ssh-rsa AAAA...            # additional keys
  sftp: false                    # boolean (requires username: root)
  compatibility_mode: false      # boolean (⚠️ reduces security)
  allow_agent_forwarding: false  # boolean (⚠️ security impact)
  allow_remote_port_forwarding: false  # boolean
  allow_tcp_forwarding: false    # boolean (⚠️ security impact)

# Shell Environment
zsh: true                        # boolean (false = bash)
share_sessions: true             # boolean (web ↔ ssh sharing)

# Customization
packages:                        # array (Alpine packages)
  - build-base
  - python3
  - nodejs
  
init_commands:                   # array (startup commands)
  - ls -la
  - echo "Welcome to HA SSH"
```

## Configuration Reference

### `log_level`
```yaml
log_level: info  # Default
```

| Level | Description | Debug Mode |
|-------|-------------|------------|
| `trace` | All internal functions | ✅ Single connection |
| `debug` | Detailed debug info | ✅ Single connection |
| `info` | Normal events | ❌ |
| `warning` | Non-error exceptions | ❌ |
| `error` | Runtime errors | ❌ |
| `fatal` | System unusable | ❌ |

> Levels are hierarchical (debug includes info, etc.)

### `ssh` Group

| Option | Type | Default | Requirements | Security Impact |
|--------|------|---------|--------------|----------------|
| `username` | string | - | Lowercase, `root` for SFTP | - |
| `password` | string | `""` | Empty = disabled | ⚠️ Not recommended |
| `authorized_keys` | array | `[]` | SSH public keys | ✅ Recommended |
| `sftp` | boolean | `false` | `username: root` | - |
| `compatibility_mode` | boolean | `false` | - | ⚠️ Reduces security |
| `allow_agent_forwarding` | boolean | `false` | - | ⚠️ Minor risk |
| `allow_remote_port_forwarding` | boolean | `false` | - | - |
| `allow_tcp_forwarding` | boolean | `false` | - | ⚠️ Minor risk |

#### Authentication Examples
```yaml
# Recommended: SSH Keys
ssh:
  username: homeassistant
  authorized_keys:
    - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA...
    - ssh-rsa AAAAB3NzaC1yc2EAAAA...

# SFTP Support
ssh:
  username: root  # Required
  sftp: true
```

### Shell & Environment Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `zsh` | boolean | `true` | Use ZSH (false = Bash) |
| `share_sessions` | boolean | `true` | Web ↔ SSH session sharing |
| `packages` | array | `[]` | Alpine packages to install |
| `init_commands` | array | `[]` | Startup commands |

#### Environment Examples
```yaml
# Custom shell with packages
zsh: false  # Use Bash
packages:
  - python3
  - python3-pip
  - nodejs
  - npm
  - htop
  
init_commands:
  - pip install --upgrade pip
  - npm install -g npm
  - echo "Environment ready"

# Isolated sessions
share_sessions: false  # Separate web/SSH sessions
```

## Limitations

| Feature | Requirement |
|---------|-------------|
| SFTP | `username: root` |
| rsync | `username: root` |

## References

- **Repository**: [hassio-addons/addon-ssh](https://github.com/hassio-addons/addon-ssh)
- **Releases**: [GitHub Releases](https://github.com/hassio-addons/addon-ssh/releases) (Semantic Versioning)
- **Issues**: [GitHub Issues](https://github.com/hassio-addons/addon-ssh/issues)
- **Contributors**: [Contributors Page](https://github.com/hassio-addons/addon-ssh/graphs/contributors)

### Support Channels
- [HA Community Add-ons Discord](https://discord.me/hassioaddons)
- [Home Assistant Discord](https://discord.gg/c5DvZ4e) 
- [Community Forum](https://community.home-assistant.io/)
- [r/homeassistant](https://reddit.com/r/homeassistant)

---

**License**: MIT | **Author**: Franck Nijhof | **Copyright**: 2017-2025