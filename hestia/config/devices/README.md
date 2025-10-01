# TEMPLATE: Device Configuration Files
# 
# This directory contains device configuration files that may include:
# - IP addresses (private network ranges)
# - MAC addresses (hardware identifiers)  
# - Device serial numbers
# - Network credentials references
#
# These files are excluded from git tracking for privacy protection.
# 
# Template structure for device configs:
# ---
# as_built:
#   name: "Device Name - Description"
#   change_date: "YYYY-MM-DD"
#   device:
#     vendor: "Vendor Name"
#     model: "Model Number"
#     firmware: "Version"
#     mgmt_ip: "__IP_ADDRESS__"
#     ui_access: "__REDACTED__"
#   network:
#     ip: "__IP_ADDRESS__"
#     mac: "__MAC_ADDRESS__"
#     vlan: "__VLAN_ID__"
#
# Replace __PLACEHOLDER__ values with actual configuration data.
# These files contain PII and are automatically excluded from git tracking.

# Example device types that should have .conf files:
# - broadlink.conf
# - nas.conf  
# - netgear.conf
# - localtuya.conf
# - hifi.conf
# - lights.conf
# - motion.conf
# - media.conf
# - valetudo.conf