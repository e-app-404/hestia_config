#!/bin/bash
# Backup Agent Validator for Synology DSM
# Tests connectivity and authentication for backup agents

set -euo pipefail

SYNOLOGY_HOST="192.168.0.104"
SYNOLOGY_PORT="5000"
BACKUP_CONFIG="/config/.storage/backup"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

test_connectivity() {
    log_info "Testing connectivity to Synology NAS at $SYNOLOGY_HOST..."
    if ping -c 3 "$SYNOLOGY_HOST" > /dev/null 2>&1; then
        log_info "✓ Connectivity test passed"
        return 0
    else
        log_error "✗ Cannot reach Synology NAS at $SYNOLOGY_HOST"
        return 1
    fi
}

test_api_access() {
    log_info "Testing Synology API access..."
    local response
    response=$(curl -s -m 10 "http://$SYNOLOGY_HOST:$SYNOLOGY_PORT/webapi/entry.cgi?api=SYNO.API.Info&version=1&method=query&query=SYNO.FileStation.Info" 2>/dev/null || echo "")
    
    if echo "$response" | grep -q '"success":true'; then
        log_info "✓ API access test passed"
        return 0
    else
        log_error "✗ API access failed: $response"
        return 1
    fi
}

check_backup_config() {
    log_info "Checking backup configuration..."
    
    if [[ ! -f "$BACKUP_CONFIG" ]]; then
        log_error "✗ Backup configuration file not found: $BACKUP_CONFIG"
        return 1
    fi
    
    # Extract synology agent configuration
    local synology_agent
    synology_agent=$(jq -r '.data.config.agents | to_entries[] | select(.key | startswith("synology_dsm")) | .key' "$BACKUP_CONFIG" 2>/dev/null || echo "")
    
    if [[ -z "$synology_agent" ]]; then
        log_warn "No Synology DSM backup agent found in configuration"
        return 1
    fi
    
    log_info "✓ Found Synology backup agent: $synology_agent"
    
    # Check for failed backups
    local failed_count
    failed_count=$(jq -r "[.data.backups[] | select(.failed_agent_ids[] == \"$synology_agent\")] | length" "$BACKUP_CONFIG" 2>/dev/null || echo "0")
    
    if [[ "$failed_count" -gt 0 ]]; then
        log_warn "Found $failed_count backup(s) with failed uploads to Synology"
        return 1
    else
        log_info "✓ No recent backup failures detected"
        return 0
    fi
}

suggest_fixes() {
    log_info "Suggested fixes for Synology backup upload issues:"
    echo
    echo "1. Check Synology DSM user account:"
    echo "   - Verify 'homeassistant' user exists and is enabled"
    echo "   - Ensure user has FileStation privileges"
    echo "   - Check if 2FA/MFA is enabled (may need to disable for backup agent)"
    echo
    echo "2. Verify backup path permissions:"
    echo "   - Ensure /homes/homeassistant/ha_backup_home exists"
    echo "   - Check write permissions for 'homeassistant' user"
    echo "   - Verify sufficient disk space"
    echo
    echo "3. Network and authentication:"
    echo "   - Check firewall settings on Synology NAS"
    echo "   - Verify HTTP service is enabled (not HTTPS only)"
    echo "   - Test manual file upload to the backup path"
    echo
    echo "4. Home Assistant integration:"
    echo "   - Reconfigure Synology DSM integration"
    echo "   - Remove and re-add backup agent"
    echo "   - Check integration logs for specific error messages"
}

main() {
    log_info "Starting Synology DSM backup agent validation..."
    echo
    
    local exit_code=0
    
    test_connectivity || exit_code=1
    test_api_access || exit_code=1
    check_backup_config || exit_code=1
    
    echo
    if [[ $exit_code -eq 0 ]]; then
        log_info "All tests passed - backup agent should be working"
    else
        log_error "One or more tests failed - backup uploads may fail"
        echo
        suggest_fixes
    fi
    
    return $exit_code
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi