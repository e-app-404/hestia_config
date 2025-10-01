# TEMPLATE: System Configuration Files  
#
# This directory contains system-level configuration files that may include:
# - System relationships and topology
# - CLI command templates with credentials
# - Transient state information
# - Network relationship mappings
#
# These files are excluded from git tracking for security.
#
# Template structure for system configs:
# ---
# system:
#   relationships:
#     devices:
#       router:
#         lan_ipv4: "__ROUTER_IP__"
#         mgmt_url: "__MANAGEMENT_URL__"
#   cli:
#     commands:
#       mount_config: "mount command with __CREDENTIALS__"
#
# Replace __PLACEHOLDER__ values with actual system configuration.
# These files may contain credentials and network PII.

# Example system configuration files:
# - cli.conf (CLI commands and credentials)
# - relationships.conf (network topology and relationships)  
# - transient_state.conf (temporary state information)
#
# Exception: hestia_workspace.conf is tracked as it contains only schema definitions.