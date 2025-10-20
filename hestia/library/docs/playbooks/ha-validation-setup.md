# Home Assistant Configuration Validation Setup

This document explains how to set up proper Home Assistant core validation for the ADR-0024 compliance tasks.

## Current Status

✅ **Basic validation is working** - YAML syntax and command testing passes
⚠️ **Full HA core validation requires setup** - SSH or API access needed

## Validation Methods (Priority Order)

### 1. 🥇 SSH + `ha core check` (Recommended)

**Setup:**
1. Install the "SSH & Web Terminal" addon in Home Assistant
2. Configure SSH authentication (password or key-based)
3. Add SSH host configuration
4. Test connection

**Command:** `ssh hass 'ha core check'`

### 2. 🥈 Home Assistant API (Alternative)

**Setup:**
1. Create a long-lived access token in Home Assistant
2. Set `HA_TOKEN` environment variable
3. API validation will be attempted automatically

**Command:** Uses REST API endpoints for configuration validation

### 3. 🥉 Docker (Fallback)

**Requirements:**
- Docker installed and running
- Uses official Home Assistant container for validation

**Command:** `docker run --rm -v /config:/config ghcr.io/home-assistant/home-assistant:stable python -m homeassistant --script check_config -c /config`

### 4. 📋 Simple Validation (Current Fallback)

**What it does:**
- YAML syntax validation
- Configuration structure verification  
- Command execution testing
- Basic include directive checks

**Limitations:**
- Cannot validate Home Assistant-specific integrations
- No entity relationship validation
- No automation/script syntax validation

## Quick Setup

### Option A: SSH Access (Recommended)

1. Run the setup guide:
   ```bash
   /config/bin/setup-ha-ssh
   ```

2. Follow the displayed instructions to:
   - Install SSH & Web Terminal addon
   - Configure authentication
   - Add SSH host configuration

3. Test the connection:
   ```bash
   ssh hass 'ha core check'
   ```

### Option B: API Token

1. In Home Assistant, go to Profile → Long-lived access tokens
2. Create a new token
3. Set the environment variable:
   ```bash
   export HA_TOKEN="your_token_here"
   ```

## VS Code Tasks

- **ADR-0024: Setup HA SSH Access** - Guides you through SSH setup
- **ADR-0024: Validate HA YAML & Core** - Runs validation with best available method
- **ADR-0024: Full Setup & Verify** - Complete setup and validation sequence

## Troubleshooting

### SSH Connection Issues

```bash
# Test SSH connectivity
ssh -v -p 22222 root@homeassistant.local

# Check if SSH addon is running
curl -s http://homeassistant.local:8123/api/

# Test port accessibility
nc -z homeassistant.local 22222
```

### API Access Issues

```bash
# Test API with token
curl -H "Authorization: Bearer $HA_TOKEN" http://homeassistant.local:8123/api/

# Verify token in HA UI
```

### Docker Issues

```bash
# Test Docker
docker --version

# Pull HA container
docker pull ghcr.io/home-assistant/home-assistant:stable
```

## Files

- `/config/bin/config-validate` - Main validation script with fallback chain
- `/config/bin/config-validate-simple` - Simple validation fallback
- `/config/bin/config-validate-api` - API-based validation (requires HA_TOKEN)
- `/config/bin/setup-ha-ssh` - SSH setup guide and testing
- `/config/.vscode/tasks.json` - VS Code task definitions

## Benefits of Full Validation

**SSH + `ha core check`:**
- ✅ Complete integration validation
- ✅ Entity relationship checks  
- ✅ Automation/script syntax validation
- ✅ Custom component compatibility
- ✅ Real-time configuration testing

**Simple validation (current):**
- ✅ YAML syntax validation
- ✅ File structure verification
- ✅ Command execution testing
- ❌ No integration validation
- ❌ No entity relationship checks