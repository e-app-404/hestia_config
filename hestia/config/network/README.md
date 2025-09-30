# TEMPLATE: Network Configuration Files
#
# This directory contains network configuration files that may include:
# - Network topology information
# - IP address ranges and subnets
# - DNS server configurations
# - VLAN configurations
# - Router and switch configurations
# - Cloudflare tunnel configurations
#
# These files are excluded from git tracking for security and privacy.
#
# Template structure for network configs:
# ---
# _meta:
#   project: "Network Component"
#   domain: "network/component_name"
#   version: "1.0"
#   generated_utc: "YYYY-MM-DDTHH:MM:SSZ"
# 
# network:
#   ip_ranges:
#     - "__SUBNET__/__CIDR__"
#   gateway: "__GATEWAY_IP__"
#   dns_servers:
#     - "__DNS_SERVER_IP__"
#   vlan_config:
#     management: "__VLAN_ID__"
#
# Replace __PLACEHOLDER__ values with actual network configuration.
# These files contain network topology PII and are excluded from git tracking.

# Example network configuration files:
# - cloudflare.conf
# - nas.conf
# - netgear.conf  
# - network.conf